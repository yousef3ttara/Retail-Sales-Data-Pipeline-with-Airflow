# 🚀 Retail Sales Data Pipeline with Apache Airflow

A complete **Data Engineering ETL Pipeline** built using **Python, Azure Blob Storage, SQL Server, and Apache Airflow** following the **Medallion Architecture (Bronze → Silver → Gold)**.

The pipeline automates data ingestion, validation, transformation, loading, monitoring, and scheduling to produce analytics-ready datasets from raw retail sales data.

---

# 📌 Project Overview

This project demonstrates an end-to-end modern Data Engineering workflow.

The pipeline performs the following steps:

1. Read raw CSV datasets
2. Upload data to Azure Blob Storage as Parquet (Bronze Layer)
3. Validate data quality
4. Clean and transform the data (Silver Layer)
5. Load analytical tables into SQL Server (Gold Layer)
6. Automate the entire workflow using Apache Airflow

---

# 🏗️ Architecture

```
                 Raw CSV Files
                       │
                       ▼
             Bronze Layer (Azure Blob)
        Raw Parquet files stored in Azure
                       │
                       ▼
              Data Validation Checks
                       │
                       ▼
             Silver Layer (Azure Blob)
        Cleaned & Standardized Parquet
                       │
                       ▼
             Gold Layer (SQL Server)
      Fact Tables + Dimension Tables
```

---

# ⚙️ Tech Stack

- Python
- Apache Airflow
- Azure Blob Storage
- SQL Server
- Pandas
- PyArrow
- SQLAlchemy
- PyODBC
- python-dotenv

---

# 📂 Project Structure

```
Retail-Sales-Data-Pipeline-with-Airflow/

│
├── airflow/
│   ├── dags/
│   │      retail_pipeline_dag.py
│   │
│   └── tasks/
│          ingest.py
│          validate.py
│          transform.py
│          load_gold.py
│          drift_check.py
│          utils.py
│
├── sql/
│      create_schema.sql
│      create_views.sql
│
├── data/
│      raw/
│
├── requirements.txt
│
├── .env
│
└── README.md
```

---

# 🏅 Medallion Architecture

## 🟤 Bronze Layer

### Purpose

- Store raw source data
- Preserve original datasets
- Convert CSV files into Parquet
- Upload data to Azure Blob Storage

### Output

```
bronze/
    daily_sales.parquet
    dealers.parquet
    recalls.parquet
    sentiment.parquet
    car_models.parquet
    sales_by_model.parquet
```

---

## ⚪ Silver Layer

### Purpose

- Clean data
- Handle missing values
- Remove duplicates
- Standardize formats
- Prepare high-quality datasets

### Output

```
silver/
    cleaned parquet files
```

---

## 🟡 Gold Layer

### Purpose

Build an analytical data warehouse inside SQL Server.

### Includes

- Fact Tables
- Dimension Tables
- SQL Views

### Used For

- Data Warehousing
- Analytical Queries
- Business Reporting
- Downstream Data Consumption

---

# 🔄 ETL Workflow

```
Extract
    ↓
CSV Files

Transform
    ↓
Validation
Cleaning
Standardization

Load
    ↓
Azure Blob Storage
    ↓
SQL Server
```

---

# 📊 Pipeline Flow

```
CSV Files
    │
    ▼
ingest.py
    │
    ▼
validate.py
    │
    ▼
drift_check.py
    │
    ▼
transform.py
    │
    ▼
load_gold.py
```

Apache Airflow orchestrates the execution of every stage automatically.

---

# 📋 Airflow DAG

The pipeline is managed using Apache Airflow.

Tasks execute in the following order:

```
Ingest Bronze
      │
      ▼
Validate Bronze
      │
      ▼
Drift Detection
      │
      ▼
Transform Silver
      │
      ▼
Load Gold
      │
      ▼
Success Notification
```

---

# ✨ Features

- End-to-End ETL Pipeline
- Azure Blob Storage Integration
- Apache Airflow Orchestration
- Data Validation
- Data Cleaning
- Data Drift Detection
- Structured Logging
- SQL Server Integration
- Star Schema Design
- Automated Scheduling
- Email Notifications

---

# 📊 Data Quality Checks

The pipeline validates:

- Empty datasets
- Duplicate records
- Missing foreign keys
- Invalid relationships
- Row count consistency
- Null percentage
- Data drift detection

Execution stops automatically if critical errors are detected.

---

# 📦 Installation

Clone the repository

```bash
git clone https://github.com/yousef3ttara/Retail-Sales-Data-Pipeline-with-Airflow.git

cd Retail-Sales-Data-Pipeline-with-Airflow
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
AZURE_CONN_STR=YOUR_CONNECTION_STRING

AZURE_CONTAINER=retail-pipeline

SQL_SERVER=your_server

SQL_DATABASE=retail_db

SQL_USER=username

SQL_PASSWORD=password
```

---

# ▶️ Running the Pipeline

Run each stage individually:

```bash
python airflow/tasks/ingest.py
```

```bash
python airflow/tasks/validate.py
```

```bash
python airflow/tasks/transform.py
```

```bash
python airflow/tasks/load_gold.py
```

Or run the complete pipeline using Apache Airflow.

---

# 📚 Learning Outcomes

This project demonstrates practical experience with:

- Data Engineering
- ETL Pipelines
- Azure Blob Storage
- SQL Data Warehousing
- Apache Airflow
- Data Validation
- Medallion Architecture
- Pipeline Automation
- Cloud Data Storage

---

# 👥 Project Team

Developed by:

- **Malak Mohamed** *(Team Leader)*
- **Yousef Ragab**
- **Mohamed Essam**
- **Zeinab Roushdy**
- **Basmala Waheed**
- **Nagy Mohamed**

---

# ⭐ If you found this project useful, don't forget to give it a Star!
