import os
import json
import pandas as pd

# Configure base directory relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def profile_csv(file_path):
    """Profiles a CSV file and returns structural and statistical metadata."""
    df = pd.read_csv(file_path)
    total_records = len(df)
    total_columns = len(df.columns)
    
    # Calculate duplicates (entire rows and based on primary keys)
    dup_rows = df.duplicated().sum()
    pk_dup = df.duplicated(subset=["customer_id"]).sum() if "customer_id" in df.columns else 0
    
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_usage_str = f"{memory_bytes / 1024:.2f} KB"
    
    # Column specific profiling
    col_profiles = []
    for col in df.columns:
        col_type = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        try:
            unique_count = df[col].nunique()
        except TypeError:
            unique_count = "N/A (Nested List)"
        col_profiles.append({
            "Column": col,
            "DataType": col_type,
            "Null Count": null_count,
            "Unique Count": unique_count
        })
        
    df_cols = pd.DataFrame(col_profiles)
    
    # Numeric column statistics
    numeric_cols = df.select_dtypes(include=["number"])
    if not numeric_cols.empty:
        stats = numeric_cols.describe().transpose().reset_index()
        stats = stats.rename(columns={"index": "Column"})
    else:
        stats = None
        
    return {
        "total_records": total_records,
        "total_columns": total_columns,
        "dup_rows": dup_rows,
        "pk_dup": pk_dup,
        "memory_usage": memory_usage_str,
        "columns": df_cols,
        "statistics": stats
    }

def profile_json(file_path):
    """Profiles a JSON file and returns structural and statistical metadata."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    total_records = len(df)
    total_columns = len(df.columns)
    
    # Duplicates check
    dup_rows = df.astype(str).duplicated().sum()
    pk_dup = df.duplicated(subset=["transaction_id"]).sum() if "transaction_id" in df.columns else 0
    
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_usage_str = f"{memory_bytes / 1024:.2f} KB"
    
    # Column profiles
    col_profiles = []
    for col in df.columns:
        col_type = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        try:
            unique_count = df[col].nunique()
        except TypeError:
            unique_count = "N/A (Nested List)"
        col_profiles.append({
            "Column": col,
            "DataType": col_type,
            "Null Count": null_count,
            "Unique Count": unique_count
        })
        
    df_cols = pd.DataFrame(col_profiles)
    
    # In JSON amount may be non-numeric (since we injected string values for testing)
    # Let's coerce amount to numeric for stats profiling
    df_clean = df.copy()
    df_clean["amount_numeric"] = pd.to_numeric(df_clean["amount"], errors="coerce")
    stats = df_clean[["amount_numeric"]].describe().transpose().reset_index()
    stats = stats.rename(columns={"index": "Column"})
    
    return {
        "total_records": total_records,
        "total_columns": total_columns,
        "dup_rows": dup_rows,
        "pk_dup": pk_dup,
        "memory_usage": memory_usage_str,
        "columns": df_cols,
        "statistics": stats
    }

def generate_report():
    """Compiles the profiles of CSV and JSON datasets into a Markdown report."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    cust_path = os.path.join(DATASETS_DIR, "customers.csv")
    txn_path = os.path.join(DATASETS_DIR, "transactions.json")
    config_path = os.path.join(DATASETS_DIR, "config.txt")
    
    customers_profile = profile_csv(cust_path)
    transactions_profile = profile_json(txn_path)
    
    report_content = f"""# Data Schema Profiling Report

This report summarizes the data profiling metrics and inferred schemas of the incoming files.

---

## 1. Customers Dataset Profile (`datasets/customers.csv`)

### Summary Metrics
| Metric | Value |
| :--- | :--- |
| **Total Records** | {customers_profile["total_records"]} |
| **Total Columns** | {customers_profile["total_columns"]} |
| **Duplicate Rows (Exact)** | {customers_profile["dup_rows"]} |
| **Duplicate Primary Keys (`customer_id`)** | {customers_profile["pk_dup"]} |
| **Memory Footprint** | {customers_profile["memory_usage"]} |

### Column Schemas & Missing Values
{customers_profile["columns"].to_markdown(index=False)}

---

## 2. Transactions Dataset Profile (`datasets/transactions.json`)

### Summary Metrics
| Metric | Value |
| :--- | :--- |
| **Total Records** | {transactions_profile["total_records"]} |
| **Total Columns** | {transactions_profile["total_columns"]} |
| **Duplicate Rows (Exact)** | {transactions_profile["dup_rows"]} |
| **Duplicate Primary Keys (`transaction_id`)** | {transactions_profile["pk_dup"]} |
| **Memory Footprint** | {transactions_profile["memory_usage"]} |

### Column Schemas & Missing Values
{transactions_profile["columns"].to_markdown(index=False)}

### Numerical Summary Statistics (Coerced Numeric)
{transactions_profile["statistics"].to_markdown(index=False)}

---

## 3. Configuration Source Overview (`datasets/config.txt`)

Below is the raw unstructured key-value settings ingested from the source environment:
```ini
{open(config_path, "r").read()}
```
"""
    
    report_file = os.path.join(OUTPUT_DIR, "data_profile_summary.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Schema profiling completed. Report written to {report_file}")

if __name__ == "__main__":
    generate_report()
