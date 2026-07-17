# Data Quality and Ingestion Validation Report

This report summarizes the data quality checks, structural validation outcomes, and quarantine statistics for Practical 2 Ingestion pipelines.

---

## 1. Customer Records Validation Summary

| Category | Record Count | Percentage |
| :--- | :---: | :---: |
| **Total Ingested Records** | 100 | 100.0% |
| **Clean Accepted Records** | 86 | 86.0% |
| **Quarantined Records** | 14 | 14.0% |

### Discovered Customer Validation Failures
| Failure Reason | Occurrences |
| :--- | :---: |
| Missing Required Fields (Null values) | 5 |
| Duplicate Primary Key (`customer_id`) | 5 |
| Malformed Email Addresses (Regex match failure) | 4 |

*Failed customer records have been isolated and written to `datasets/quarantined_customers.csv`.*

---

## 2. Transaction Records Validation Summary

| Category | Record Count | Percentage |
| :--- | :---: | :---: |
| **Total Ingested Records** | 150 | 100.0% |
| **Clean Accepted Records** | 124 | 82.7% |
| **Quarantined Records** | 26 | 17.3% |

### Discovered Transaction Validation Failures
| Failure Reason | Occurrences |
| :--- | :---: |
| Missing Primary Keys / Customer Links | 5 |
| Duplicate Primary Key (`transaction_id`) | 0 |
| Non-numeric / Negative Amount Values | 5 |
| Referential Integrity Violations (Unknown Customer link) | 16 |

*Failed transaction records have been isolated and written to `datasets/quarantined_transactions.json`.*

---

## 3. Supplementary Ingestion Validation Summary (Messy User Files)

| Category | Record Count | Percentage |
| :--- | :---: | :---: |
| **Total Input Records** | 7 | 100.0% |
| **Clean Accepted Records** | 4 | 57.1% |
| **Quarantined Records (Missing `user_id` Primary Key)** | 3 | 42.9% |

*Failed messy user records have been isolated and written to `datasets/quarantined_messy_users.csv`.*

---

## 4. Data Quality Pipeline Execution Log

Below is the complete audit execution log recorded by the python logging module during runtime:

```text
2026-07-17 10:56:17,045 [INFO] - === Starting Data Quality Pipeline Process ===
2026-07-17 10:56:17,045 [INFO] - === Starting Customer Validation & Cleaning ===
2026-07-17 10:56:17,053 [WARNING] - Customer CUST0005: Quarantined - Missing required profile fields (name/email/phone).
2026-07-17 10:56:17,055 [WARNING] - Customer CUST0012: Quarantined - Missing required profile fields (name/email/phone).
2026-07-17 10:56:17,056 [WARNING] - Customer CUST0004: Quarantined - Duplicate customer_id found.
2026-07-17 10:56:17,057 [WARNING] - Customer CUST0029: Quarantined - Duplicate customer_id found.
2026-07-17 10:56:17,058 [WARNING] - Customer CUST0030: Quarantined - Malformed email address: 'testemail.com'
2026-07-17 10:56:17,059 [WARNING] - Customer CUST0036: Quarantined - Duplicate customer_id found.
2026-07-17 10:56:17,061 [WARNING] - Customer CUST0065: Quarantined - Malformed email address: 'john.doe@'
2026-07-17 10:56:17,063 [WARNING] - Customer CUST0070: Quarantined - Missing required profile fields (name/email/phone).
2026-07-17 10:56:17,063 [WARNING] - Customer CUST0072: Quarantined - Malformed email address: 'invalid-email-format'
2026-07-17 10:56:17,064 [WARNING] - Customer CUST0076: Quarantined - Missing required profile fields (name/email/phone).
2026-07-17 10:56:17,065 [WARNING] - Customer CUST0078: Quarantined - Malformed email address: 'alex @domain.com'
2026-07-17 10:56:17,066 [WARNING] - Customer CUST0082: Quarantined - Duplicate customer_id found.
2026-07-17 10:56:17,066 [WARNING] - Customer CUST0087: Quarantined - Missing required profile fields (name/email/phone).
2026-07-17 10:56:17,067 [WARNING] - Customer CUST0004: Quarantined - Duplicate customer_id found.
2026-07-17 10:56:17,069 [INFO] - Wrote 14 quarantined customer records to C:\Users\Hit\Desktop\5th SEM\DE\Practical-02-Data-Sources-and-Data-Generation\datasets\quarantined_customers.csv
2026-07-17 10:56:17,069 [INFO] - Customer validation completed: 86 clean, 14 quarantined of 100 total.
2026-07-17 10:56:17,069 [INFO] - === Starting Transactions Validation & Cleaning ===
2026-07-17 10:56:17,070 [ERROR] - Transaction TXN00001: Referential Integrity Failure - Customer ID 'CUST0076' does not exist in clean customer database.
2026-07-17 10:56:17,070 [ERROR] - Transaction TXN00007: Referential Integrity Failure - Customer ID 'CUST0078' does not exist in clean customer database.
2026-07-17 10:56:17,070 [WARNING] - Transaction index 11: Quarantined - Missing transaction_id or customer_id.
2026-07-17 10:56:17,070 [ERROR] - Transaction TXN00015: Referential Integrity Failure - Customer ID 'CUST0065' does not exist in clean customer database.
2026-07-17 10:56:17,070 [WARNING] - Transaction TXN00016: Quarantined - Amount must be positive: -100.5
2026-07-17 10:56:17,071 [WARNING] - Transaction TXN00028: Quarantined - Amount must be positive: -100.5
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00058: Referential Integrity Failure - Customer ID 'CUST0012' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00064: Referential Integrity Failure - Customer ID 'CUST0072' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00070: Referential Integrity Failure - Customer ID 'CUST0078' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00096: Referential Integrity Failure - Customer ID 'CUST0072' does not exist in clean customer database.
2026-07-17 10:56:17,071 [WARNING] - Transaction TXN00103: Quarantined - Amount must be positive: -100.5
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00104: Referential Integrity Failure - Customer ID 'CUST0070' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00105: Referential Integrity Failure - Customer ID 'CUST0087' does not exist in clean customer database.
2026-07-17 10:56:17,071 [WARNING] - Transaction TXN00110: Quarantined - Non-numeric amount value: 'INVALID_NUMERIC'
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00113: Referential Integrity Failure - Customer ID 'CUST0012' does not exist in clean customer database.
2026-07-17 10:56:17,071 [WARNING] - Transaction index 114: Quarantined - Missing transaction_id or customer_id.
2026-07-17 10:56:17,071 [WARNING] - Transaction index 115: Quarantined - Missing transaction_id or customer_id.
2026-07-17 10:56:17,071 [WARNING] - Transaction index 117: Quarantined - Missing transaction_id or customer_id.
2026-07-17 10:56:17,071 [WARNING] - Transaction TXN00123: Quarantined - Non-numeric amount value: 'INVALID_NUMERIC'
2026-07-17 10:56:17,071 [WARNING] - Transaction index 131: Quarantined - Missing transaction_id or customer_id.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00133: Referential Integrity Failure - Customer ID 'CUST0087' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00134: Referential Integrity Failure - Customer ID 'CUST0005' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00137: Referential Integrity Failure - Customer ID 'CUST0072' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00144: Referential Integrity Failure - Customer ID 'CUST0012' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00146: Referential Integrity Failure - Customer ID 'CUST0076' does not exist in clean customer database.
2026-07-17 10:56:17,071 [ERROR] - Transaction TXN00149: Referential Integrity Failure - Customer ID 'CUST0076' does not exist in clean customer database.
2026-07-17 10:56:17,073 [INFO] - Wrote 26 quarantined transaction records to C:\Users\Hit\Desktop\5th SEM\DE\Practical-02-Data-Sources-and-Data-Generation\datasets\quarantined_transactions.json
2026-07-17 10:56:17,073 [INFO] - Transaction validation completed: 124 clean, 26 quarantined of 150 total.
2026-07-17 10:56:17,073 [INFO] - === Starting Supplementary Ingestion Validation Routine ===
2026-07-17 10:56:17,073 [INFO] - Parsing supplementary input file: messy_users_1.csv
2026-07-17 10:56:17,077 [WARNING] - File 'messy_users_1.csv' Row 3: Quarantined - Missing primary key 'user_id'.
2026-07-17 10:56:17,078 [WARNING] - File 'messy_users_1.csv' Row 5: Quarantined - Missing primary key 'user_id'.
2026-07-17 10:56:17,078 [INFO] - Parsing supplementary input file: messy_users_2.json
2026-07-17 10:56:17,079 [WARNING] - File 'messy_users_2.json' Item 2: Quarantined - Missing primary key 'user_id'.
2026-07-17 10:56:17,079 [INFO] - Processed 4 clean messy records. Saved to C:\Users\Hit\Desktop\5th SEM\DE\Practical-02-Data-Sources-and-Data-Generation\datasets\clean_messy_users.csv
2026-07-17 10:56:17,080 [INFO] - Isolated 3 quarantined messy records. Saved to C:\Users\Hit\Desktop\5th SEM\DE\Practical-02-Data-Sources-and-Data-Generation\datasets\quarantined_messy_users.csv
2026-07-17 10:56:17,080 [INFO] - === Supplementary Ingestion Validation Routine Completed ===
2026-07-17 10:56:17,080 [INFO] - === Starting SQLite Database Ingestion ===
2026-07-17 10:56:17,084 [INFO] - Successfully committed transactions to SQLite. Loaded 86 customers and 124 transactions.

```
