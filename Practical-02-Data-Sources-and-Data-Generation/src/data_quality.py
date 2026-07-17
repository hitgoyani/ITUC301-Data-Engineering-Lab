import os
import re
import csv
import json
import sqlite3
import logging
import pandas as pd

# Configure base directory relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure pipeline logger to write to logs/data_quality.log
logger = logging.getLogger("DataQualityPipeline")
logger.setLevel(logging.DEBUG)

# File handler for logs/data_quality.log
log_file_path = os.path.join(LOGS_DIR, "data_quality.log")
file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Stream handler to display in console during runs
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def clean_and_validate_customers():
    """Reads customers, cleans whitespace, validates fields, and routes to quarantine or clean list."""
    logger.info("=== Starting Customer Validation & Cleaning ===")
    
    csv_src = os.path.join(DATASETS_DIR, "customers.csv")
    if not os.path.exists(csv_src):
        logger.error(f"Source customers.csv not found at {csv_src}")
        return [], []
        
    df = pd.read_csv(csv_src, dtype=str).fillna("")
    
    clean_customers = []
    quarantined_customers = []
    seen_cust_ids = set()
    
    stats = {
        "total": len(df),
        "clean": 0,
        "duplicate_id": 0,
        "missing_fields": 0,
        "malformed_email": 0
    }
    
    for idx, row in df.iterrows():
        cust_id = row["customer_id"].strip()
        name = row["name"].strip()
        email = row["email"].strip()
        phone = row["phone"].strip()
        city = row["city"].strip()
        
        # Check 1: Null or empty primary key/required fields
        if not cust_id:
            logger.warning(f"Row {idx+2}: Quarantined - Missing customer_id.")
            stats["missing_fields"] += 1
            quarantined_customers.append(dict(row))
            continue
            
        if not name or not email or not phone:
            logger.warning(f"Customer {cust_id}: Quarantined - Missing required profile fields (name/email/phone).")
            stats["missing_fields"] += 1
            row["quarantine_reason"] = "Missing required profile fields"
            quarantined_customers.append(dict(row))
            continue
            
        # Check 2: Duplicate Primary Key
        if cust_id in seen_cust_ids:
            logger.warning(f"Customer {cust_id}: Quarantined - Duplicate customer_id found.")
            stats["duplicate_id"] += 1
            row["quarantine_reason"] = "Duplicate customer_id"
            quarantined_customers.append(dict(row))
            continue
            
        # Check 3: Email format regex validation
        if not EMAIL_REGEX.match(email):
            logger.warning(f"Customer {cust_id}: Quarantined - Malformed email address: '{email}'")
            stats["malformed_email"] += 1
            row["quarantine_reason"] = f"Malformed email format: '{email}'"
            quarantined_customers.append(dict(row))
            continue
            
        # Record is clean!
        seen_cust_ids.add(cust_id)
        clean_customers.append({
            "customer_id": cust_id,
            "name": name,
            "email": email,
            "phone": phone,
            "city": city
        })
        stats["clean"] += 1
        
    # Write quarantined customers to CSV
    quarantine_csv = os.path.join(DATASETS_DIR, "quarantined_customers.csv")
    if quarantined_customers:
        q_fields = list(df.columns)
        if "quarantine_reason" not in q_fields:
            q_fields.append("quarantine_reason")
            
        with open(quarantine_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=q_fields)
            writer.writeheader()
            writer.writerows(quarantined_customers)
        logger.info(f"Wrote {len(quarantined_customers)} quarantined customer records to {quarantine_csv}")
    else:
        with open(quarantine_csv, "w", newline="", encoding="utf-8") as f:
            f.write("")
            
    logger.info(f"Customer validation completed: {stats['clean']} clean, {len(quarantined_customers)} quarantined of {stats['total']} total.")
    return clean_customers, stats

def clean_and_validate_transactions(valid_customer_ids):
    """Reads transactions, validates amounts and keys, enforces referential integrity, and routes."""
    logger.info("=== Starting Transactions Validation & Cleaning ===")
    
    json_src = os.path.join(DATASETS_DIR, "transactions.json")
    if not os.path.exists(json_src):
        logger.error(f"Source transactions.json not found at {json_src}")
        return [], []
        
    with open(json_src, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    clean_transactions = []
    quarantined_transactions = []
    seen_trans_ids = set()
    
    stats = {
        "total": len(data),
        "clean": 0,
        "missing_ids": 0,
        "duplicate_id": 0,
        "invalid_amount": 0,
        "foreign_key_violation": 0
    }
    
    for idx, txn in enumerate(data):
        trans_id = str(txn.get("transaction_id", "")).strip()
        cust_id = str(txn.get("customer_id", "")).strip()
        amount_raw = txn.get("amount", "")
        date = str(txn.get("date", "")).strip()
        
        # Check 1: Missing primary key or customer_id
        if not trans_id or not cust_id:
            logger.warning(f"Transaction index {idx}: Quarantined - Missing transaction_id or customer_id.")
            stats["missing_ids"] += 1
            txn["quarantine_reason"] = "Missing transaction_id or customer_id"
            quarantined_transactions.append(txn)
            continue
            
        # Check 2: Duplicate transaction key
        if trans_id in seen_trans_ids:
            logger.warning(f"Transaction {trans_id}: Quarantined - Duplicate transaction_id.")
            stats["duplicate_id"] += 1
            txn["quarantine_reason"] = "Duplicate transaction_id"
            quarantined_transactions.append(txn)
            continue
            
        # Check 3: Invalid numeric or negative amount
        try:
            amount = float(amount_raw)
            if amount <= 0:
                logger.warning(f"Transaction {trans_id}: Quarantined - Amount must be positive: {amount}")
                stats["invalid_amount"] += 1
                txn["quarantine_reason"] = f"Non-positive amount: {amount}"
                quarantined_transactions.append(txn)
                continue
        except (ValueError, TypeError):
            logger.warning(f"Transaction {trans_id}: Quarantined - Non-numeric amount value: '{amount_raw}'")
            stats["invalid_amount"] += 1
            txn["quarantine_reason"] = f"Non-numeric amount: '{amount_raw}'"
            quarantined_transactions.append(txn)
            continue
            
        # Check 4: Referential Integrity (Foreign Key mapping)
        if cust_id not in valid_customer_ids:
            logger.error(f"Transaction {trans_id}: Referential Integrity Failure - Customer ID '{cust_id}' does not exist in clean customer database.")
            stats["foreign_key_violation"] += 1
            txn["quarantine_reason"] = f"Referential Integrity Failure - Unknown Customer ID: '{cust_id}'"
            quarantined_transactions.append(txn)
            continue
            
        # Transaction is clean!
        seen_trans_ids.add(trans_id)
        clean_transactions.append({
            "transaction_id": trans_id,
            "customer_id": cust_id,
            "amount": amount,
            "date": date
        })
        stats["clean"] += 1
        
    # Write quarantined transactions to JSON
    quarantine_json = os.path.join(DATASETS_DIR, "quarantined_transactions.json")
    if quarantined_transactions:
        with open(quarantine_json, "w", encoding="utf-8") as f:
            json.dump(quarantined_transactions, f, indent=2)
        logger.info(f"Wrote {len(quarantined_transactions)} quarantined transaction records to {quarantine_json}")
    else:
        with open(quarantine_json, "w", encoding="utf-8") as f:
            f.write("[]")
            
    logger.info(f"Transaction validation completed: {stats['clean']} clean, {len(quarantined_transactions)} quarantined of {stats['total']} total.")
    return clean_transactions, stats

def ingest_to_sqlite(clean_customers, clean_transactions):
    """Initializes SQLite database and inserts validated clean records inside a transactional database block."""
    logger.info("=== Starting SQLite Database Ingestion ===")
    
    db_file = os.path.join(OUTPUT_DIR, "ecommerce.db")
    
    # Connect and configure database connection
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Enable foreign keys support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables with explicit constraints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            city TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT,
            amount REAL NOT NULL,
            date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        );
    """)
    
    # Ingest inside a SQL transaction block
    try:
        # Clear existing data to allow re-runs of verification
        cursor.execute("DELETE FROM transactions;")
        cursor.execute("DELETE FROM customers;")
        
        # Insert customers
        for cust in clean_customers:
            cursor.execute("""
                INSERT INTO customers (customer_id, name, email, phone, city)
                VALUES (?, ?, ?, ?, ?);
            """, (cust["customer_id"], cust["name"], cust["email"], cust["phone"], cust["city"]))
            
        # Insert transactions
        for txn in clean_transactions:
            cursor.execute("""
                INSERT INTO transactions (transaction_id, customer_id, amount, date)
                VALUES (?, ?, ?, ?);
            """, (txn["transaction_id"], txn["customer_id"], txn["amount"], txn["date"]))
            
        conn.commit()
        logger.info(f"Successfully committed transactions to SQLite. Loaded {len(clean_customers)} customers and {len(clean_transactions)} transactions.")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Failed to commit database transactions. Rolling back changes. Error: {e}")
    finally:
        conn.close()

def generate_quality_report(c_stats, t_stats):
    """Generates a summary data quality Markdown report including tables and pipeline execution log captures."""
    report_file = os.path.join(OUTPUT_DIR, "data_quality_report.md")
    
    # Read the data quality logs to include in report
    with open(log_file_path, "r", encoding="utf-8") as f:
        log_lines = f.read()
        
    report_content = f"""# Data Quality and Ingestion Validation Report

This report summarizes the data quality checks, structural validation outcomes, and quarantine statistics for Practical 2 Ingestion pipelines.

---

## 1. Customer Records Validation Summary

| Category | Record Count | Percentage |
| :--- | :---: | :---: |
| **Total Ingested Records** | {c_stats["total"]} | 100.0% |
| **Clean Accepted Records** | {c_stats["clean"]} | {c_stats["clean"]/c_stats["total"]*100:.1f}% |
| **Quarantined Records** | {c_stats["total"] - c_stats["clean"]} | {(c_stats["total"] - c_stats["clean"])/c_stats["total"]*100:.1f}% |

### Discovered Customer Validation Failures
| Failure Reason | Occurrences |
| :--- | :---: |
| Missing Required Fields (Null values) | {c_stats["missing_fields"]} |
| Duplicate Primary Key (`customer_id`) | {c_stats["duplicate_id"]} |
| Malformed Email Addresses (Regex match failure) | {c_stats["malformed_email"]} |

*Failed customer records have been isolated and written to `datasets/quarantined_customers.csv`.*

---

## 2. Transaction Records Validation Summary

| Category | Record Count | Percentage |
| :--- | :---: | :---: |
| **Total Ingested Records** | {t_stats["total"]} | 100.0% |
| **Clean Accepted Records** | {t_stats["clean"]} | {t_stats["clean"]/t_stats["total"]*100:.1f}% |
| **Quarantined Records** | {t_stats["total"] - t_stats["clean"]} | {(t_stats["total"] - t_stats["clean"])/t_stats["total"]*100:.1f}% |

### Discovered Transaction Validation Failures
| Failure Reason | Occurrences |
| :--- | :---: |
| Missing Primary Keys / Customer Links | {t_stats["missing_ids"]} |
| Duplicate Primary Key (`transaction_id`) | {t_stats["duplicate_id"]} |
| Non-numeric / Negative Amount Values | {t_stats["invalid_amount"]} |
| Referential Integrity Violations (Unknown Customer link) | {t_stats["foreign_key_violation"]} |

*Failed transaction records have been isolated and written to `datasets/quarantined_transactions.json`.*

---

## 3. Data Quality Pipeline Execution Log

Below is the complete audit execution log recorded by the python logging module during runtime:

```text
{log_lines}
```
"""
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    logger.info(f"Successfully generated data quality summary report in {report_file}")

if __name__ == "__main__":
    logger.info("=== Starting Data Quality Pipeline Process ===")
    
    # 1. Clean and validate customers
    clean_custs, cust_stats = clean_and_validate_customers()
    clean_cust_ids = {c["customer_id"] for c in clean_custs}
    
    # 2. Clean and validate transactions (injecting clean customer IDs to check ref integrity)
    clean_txns, txn_stats = clean_and_validate_transactions(clean_cust_ids)
    
    # 3. Load clean, validated records into SQLite database
    if clean_custs or clean_txns:
        ingest_to_sqlite(clean_custs, clean_txns)
        
    # 4. Generate markdown report
    generate_quality_report(cust_stats, txn_stats)
    logger.info("=== Data Quality Pipeline Process Completed ===")
