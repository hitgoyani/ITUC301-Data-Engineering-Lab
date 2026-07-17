# Data Schema Profiling Report

This report summarizes the data profiling metrics and inferred schemas of the incoming files.

---

## 1. Customers Dataset Profile (`datasets/customers.csv`)

### Summary Metrics
| Metric | Value |
| :--- | :--- |
| **Total Records** | 100 |
| **Total Columns** | 5 |
| **Duplicate Rows (Exact)** | 0 |
| **Duplicate Primary Keys (`customer_id`)** | 5 |
| **Memory Footprint** | 10.94 KB |

### Column Schemas & Missing Values
| Column      | DataType   |   Null Count |   Unique Count |
|:------------|:-----------|-------------:|---------------:|
| customer_id | str        |            0 |             95 |
| name        | str        |            3 |             97 |
| email       | str        |            1 |             99 |
| phone       | str        |            1 |             99 |
| city        | str        |            0 |            100 |

---

## 2. Transactions Dataset Profile (`datasets/transactions.json`)

### Summary Metrics
| Metric | Value |
| :--- | :--- |
| **Total Records** | 150 |
| **Total Columns** | 5 |
| **Duplicate Rows (Exact)** | 0 |
| **Duplicate Primary Keys (`transaction_id`)** | 2 |
| **Memory Footprint** | 27.54 KB |

### Column Schemas & Missing Values
| Column         | DataType   |   Null Count | Unique Count      |
|:---------------|:-----------|-------------:|:------------------|
| transaction_id | str        |            0 | 148               |
| customer_id    | str        |            0 | 75                |
| amount         | object     |            0 | 147               |
| date           | str        |            0 | 150               |
| items          | object     |            0 | N/A (Nested List) |

### Numerical Summary Statistics (Coerced Numeric)
| Column         |   count |    mean |     std |    min |     25% |     50% |    75% |     max |
|:---------------|--------:|--------:|--------:|-------:|--------:|--------:|-------:|--------:|
| amount_numeric |     148 | 400.993 | 244.641 | -100.5 | 220.537 | 374.785 | 520.88 | 1072.37 |

---

## 3. Configuration Source Overview (`datasets/config.txt`)

Below is the raw unstructured key-value settings ingested from the source environment:
```ini
# Data Engineering Ingestion Configurations
ingest_batch_size = 100
quarantine_enabled = true
sqlite_db_name = ecommerce.db
validation_level = STRICT
api_timeout_sec = 5
max_retry_attempts = 3

```
