# Practical 2: Data Sources and Data Generation

## Subject
**ITUC301 - Data Engineering**

## Practical Title
Data Sources and Data Generation

## Objective
To programmatically interface with diverse file-based, API-driven, and relational source database environments. Students will write generation engines to simulate transactional workloads, profile the incoming files to automatically discover schemas, isolate data quality violations (such as null entry leaks and format divergence), and establish appropriate operational ingestion criteria.

## Problem Definition
Write generation engines to simulate transactional workloads (synthetic customer profile tables, semi-structured API transaction logs, and unstructured configuration text files), profile the incoming datasets to automatically discover schemas, isolate data quality violations (such as null entry leaks and format divergence), and establish appropriate operational ingestion criteria.

## Dataset/Test Data
* **Customer Profile Tables:** Programmatically generated customer profiles (CustomerID, Name, Email, Country, RegistrationDate).
* **API Transaction Logs:** Semi-structured JSON payloads containing nested transactional logs (TransactionID, SessionID, ItemDetails, PaymentMethod, Amount).
* **Configuration Files:** Unstructured text files containing key-value configurations and system settings.

## Tools Required
* **Python 3.x**
* **Faker Library** (For synthetic generation of data)
* **Pandas Library** (For schema discovery, profiling, and quality validation)
* **SQLite / PostgreSQL** (For target relational database ingestion)
* **Git** (For version control)

---

## Folder Structure
```text
Practical-02-Data-Sources-and-Data-Generation/
│
├── README.md                      # Practical index, design plan, and Q&A setup
├── datasets/                      # Directory for generated raw CSV/JSON datasets (Git ignored)
├── output/                        # Directory for SQLite database and data profiling reports (Git ignored)
├── logs/                          # Directory for automated pipeline and validation logs (Git ignored)
└── src/                           # Directory for Python execution scripts
    ├── customer_generator.py      # [Planned] Synthetic customer/transaction generator script
    ├── schema_profiler.py         # [Planned] Pandas-based dataset profiling script
    └── data_quality.py            # [Planned] Validation, quality checks, and quarantine script
```

---

## Planned Python Modules

### 1. `customer_generator.py`
This module will programmatically generate synthetic records using the Python `Faker` library:
* **Customers:** Generate custom CSV records with fields: `customer_id`, `name`, `email`, `country`, and `registration_date`. It will intentionally inject a controlled rate of nulls and malformed email addresses for quality testing.
* **Transactions:** Generate nested JSON transaction entries containing transaction details, items purchased, and payment logs to simulate real-world e-commerce transaction APIs.

### 2. `schema_profiler.py`
This module will use the `pandas` library to perform automated exploratory profiling:
* Read generated datasets (CSV and JSON files).
* Discover columns, data type inferences, and count of distinct/unique values.
* Compute statistical summary descriptions (mean, min, max, standard deviation) for numeric columns.
* Identify count of missing (null) values per column.

### 3. `data_quality.py`
This module will implement data quality boundaries at the ingestion point:
* Validate primary key uniqueness and reject duplicate IDs.
* Check format requirements (e.g., regex checking for email addresses: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`).
* Isolate malformed or missing-key records, routing them to a quarantine output directory while allowing valid records to be ingested into SQLite.
* Log all activities, showing summary stats of records parsed, accepted, and quarantined.

---

## Expected Outputs
* `datasets/customers.csv`: CSV data sheet containing synthetic customer logs.
* `datasets/transactions.json`: JSON payload containing nested transaction details.
* `output/ecommerce.db`: SQLite database file populated with imported tables.
* `output/data_profile_summary.md`: Detailed markdown file detailing profile analysis results.
* `logs/data_quality.log`: Runtime execution logs reporting ingestion summary metrics.

---

## Key Questions / Analysis / Interpretation

### 1. Explain the architectural strategies used to manage severe structural schema drift when handling continuous external third-party API inputs.
*Schema drift* occurs when an external data source changes its structure (e.g., adding, renaming, deleting fields, or changing data types) without notifying downstream consumers. Strategies to manage drift include:
* **Schema-on-Read / Schema Evolution:** Loading data into semi-structured formats (JSON/Avro) within a raw data lake, allowing downstream queries to parse new fields dynamically.
* **Validation Gates (Schema Registry):** Validating incoming API payloads against registered JSON schemas at the API gateway layer, automatically quarantining invalid formats.
* **Metadata-Driven Pipelines:** Storing schema specifications in a metadata table and generating ETL jobs dynamically, preventing pipeline failures when new columns are added.

### 2. What are the structural benefits and data storage trade-offs of using semi-structured nested JSON objects over heavily normalized SQL database records?
* **Structural Benefits of JSON:** Flexibility to store complex hierarchies, nested arrays (e.g., multiple order items inside a single transaction), and sparse data without maintaining complex relational join tables. It aligns with modern app payloads and requires no rigid schema definition.
* **Trade-Offs & SQL Normalization:** Normalized SQL databases ensure strict data integrity (referential constraints) and optimize storage by reducing redundancy. In contrast, querying nested JSON in a data lake requires higher CPU overhead (parsing strings at query time) and lacks transaction guarantees unless stored in advanced engines.

### 3. How do you validate data quality at the point of ingestion without creating severe processing performance bottlenecks?
* **Asynchronous Checkpoints:** Enforcing schema checking as an out-of-band parallel pipeline step (e.g., checking data quality metrics on mini-batches in stream brokers like Kafka rather than scanning row-by-row during storage writes).
* **Vectorized In-Memory Audits:** Utilizing optimized vectorized processing libraries (like Pandas/NumPy in-memory vector blocks or Apache Arrow) to scan full batches for nulls/regex violations in milliseconds.
* **Quarantine Routing:** Routing failed checks immediately to a quarantine directory/topic instead of halting the entire pipeline, allowing valid data to continue processing.

---

## Supplementary Problem Planning

### Quarantine Validation Routine Design
To address the supplementary problem, a validation routine will be built to:
1. Scan a landing directory containing user input files.
2. Read files using Pandas dataframes.
3. Check for the existence of the primary key field. If missing or null, quarantine the record by writing it to `datasets/quarantine_records.csv`.
4. Log warning alerts to a centralized log system (`logs/data_quality.log`) whenever a record is quarantined.

---

## Key Skills
* Programmatic data profiling.
* Synthetic record generation.
* Automated quality boundary enforcement.
* Source system type evaluation.

## Applications
* Source data profiling layers.
* Raw data landing zones.
* Automated incoming payload quality gates.

## Learning Outcome
Proficiency in analyzing, classifying, and clean-profiling diverse transactional source data models prior to target system ingestion.

## Post Laboratory Work Description
Following execution in the next laboratory session, we will export automated data quality logs and compile a comprehensive report detailing validation checks and quarantine performance.
