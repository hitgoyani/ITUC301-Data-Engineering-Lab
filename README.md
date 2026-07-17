# ITUC301: Data Engineering Lab

This repository contains all the laboratory practical reports, design specifications, configurations, pipelines, and code implemented during the course **ITUC301: Data Engineering**.

## Course & Institution Details
* **Course Name:** Data Engineering
* **Course Code:** ITUC301
* **Department:** Department of Information Technology
* **Institution:** Devang Patel Institute of Advance Technology and Research (DEPSTAR)
* **University:** Charotar University of Science & Technology (CHARUSAT)
* **Author:** Hit Goyani

---

## Repository Purpose
The purpose of this repository is to systematically organize, document, and implement all 11 laboratory practicals specified in the ITUC301 Data Engineering syllabus. It serves as a unified workspace demonstrating end-to-end data pipeline construction, synthetic generation, storage design, distributed architectures, change data capture, query optimization, dimensional modeling, and serving workflows.

---

## Repository Structure
```text
ITUC301-Data-Engineering-Lab/
│
├── README.md                                  # Repository overview and practical index
├── .gitignore                                 # Excludes caches, databases, and logs
├── LICENSE                                    # MIT License
│
├── Practical-01-Data-Engineering-Lifecycle/   # Practical 1: Lifecycle mapping
│   ├── README.md                              # Lab report and analysis questions
│   ├── manifesto.md                           # System undercurrents manifesto
│   └── Data_Engineering_Lifecycle.png         # Architectural data flow diagram
│
└── Practical-02-Data-Sources-and-Data-Generation/  # Practical 2: Generator planning
    ├── README.md                              # Ingestion planning and modules design
    ├── datasets/                              # Raw and generated datasets (ignored)
    ├── output/                                # Processed pandas/sqlite outputs (ignored)
    ├── logs/                                  # Data quality logs (ignored)
    └── src/                                   # Python source scripts (planned)
```

---

## Software & Environmental Requirements
To run or inspect the code and pipelines in this laboratory workspace:
* **Operating System:** Windows/macOS/Linux
* **Version Control:** Git
* **Programming Environment:** Python 3.8+
* **Dependencies:**
  * `pandas` (for schema profiling and transformations)
  * `Faker` (for generating synthetic records)
  * `requests` (for HTTP API interaction)
  * `sqlite3` (built-in relational storage)
* **Design Tools:** Draw.io / Lucidchart (for diagramming)

---

## GitHub Usage Instructions

### 1. Cloning the Repository
Clone the repository locally using:
```bash
git clone https://github.com/hitgoyani/ITUC301-Data-Engineering-Lab.git
```

### 2. Checking Status
Check modified or untracked files:
```bash
git status
```

### 3. Committing Changes
Use professional, descriptive git commits:
```bash
git add .
git commit -m "feat(practical-01): complete Data Engineering Lifecycle documentation"
```

---

## Practical Index

| Practical No. | Practical Title | Status |
| :---: | :--- | :--- |
| **01** | **Understanding the Data Engineering Lifecycle** | **Completed & Documented** |
| **02** | **Data Sources and Data Generation** | **Project Setup & Planning Completed** |
| 03 | Batch vs Streaming Data Ingestion | Not Started |
| 04 | ETL vs ELT Pipeline Design | Not Started |
| 05 | Distributed Storage Systems | Not Started |
| 06 | Storage Lifecycle Management | Not Started |
| 07 | Change Data Capture (CDC) | Not Started |
| 08 | Query Processing and Optimization | Not Started |
| 09 | Data Modeling for Analytics | Not Started |
| 10 | Batch and Streaming Transformations | Not Started |
| 11 | Data Serving, Reverse ETL, and Security | Not Started |
