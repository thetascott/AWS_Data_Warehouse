# AWS Data Warehouse Project

Welcome to the **AWS Data Warehouse Project** repository! 
This project demonstrates a comprehensive data warehousing solution.  Designed as a portfolio project, it highlights industry best practices in data engineering and analytics.

---

## Data Architecture

The data architecture for this project follows Medallion Architecture **Bronze**, **Silver**, and **Gold** layers:
![Data Architecture](Docs/High%20Level%20Architecture.png)
1. **Bronze Layer**: Stores raw data as-is from the source systems. Data is ingested from CSV Files into a S3 bucket.
2. **Silver Layer**: This layer includes data cleansing, standardization, and normalization processes to prepare data for analysis. Transformations are performed using PySpark, and the resulting tables are stored in Parquet format for optimized performance.
3. **Gold Layer**: Houses business-ready data modeled into a star schema required for reporting and analytics.

---

## Project Overview

This project involves:

1. **Data Architecture**: Designing a Modern Data Warehouse Using Medallion Architecture **Bronze**, **Silver**, and **Gold** layers.
2. **ETL Pipelines**: Extracting, transforming, and loading data from source systems into the warehouse.
3. **Data Modeling**: Developing fact and dimension tables optimized for analytical queries.
4. **Infrastructure as Code (IaC)**: Managed AWS infrastructure using Terraform to ensure consistent, repeatable environment setup and configuration.
5. **CI/CD Automation**: Built a GitHub Actions pipeline to automate the entire process - from data ingestion to generation of the Gold Layer.

---

## Project Requirements

### Building the Data Warehouse (Data Engineering)

#### Objective
Develop a modern data warehouse using AWS services to consolidate sales data, enabling analytical reporting and informed decision-making.

#### Specifications
- **Data Sources**: Import data from two source systems (ERP and CRM) provided as CSV files.
- **Data Quality**: Cleanse and resolve data quality issues prior to analysis.
- **Integration**: Combine both sources into a single, user-friendly data model designed for analytical queries.
- **Scope**: Focus on the latest dataset only; historization of data is not required.
- **Documentation**: Provide clear documentation of the data model to support both business stakeholders and analytics teams.

---

## Repository Structure
```
aws-data-warehouse/
│
├── Datasets/                           # Raw datasets used for the project (ERP and CRM data)
│
├── Docs/                               # Project documentation and architecture details
│   ├── High Level Architecture.png     # Project's architecture
│   ├── data_catalog.md                 # Catalog of datasets, including field descriptions and metadata
│   ├── Data Flow.png                   # Data flow diagram
│   ├── Data Model.png                  # Data model (star schema)
│   ├── Data Integration.png            # Data Integration (table relationships)
│   ├── naming-conventions.md           # Consistent naming guidelines for tables, columns, and files
├── Infrastructure/                     # Terraform configurations for managing AWS infrastructure components.
│
├── Scripts/                            # SQL scripts for ETL and transformations
│   ├── bronze/                         # Scripts for extracting and loading raw data
│   ├── silver/                         # Scripts for cleaning and transforming data
│   ├── gold/                           # Scripts for creating analytical models
│
├── Tests/                              # Test scripts and quality files
│
├── README.md                           # Project overview and instructions
├── LICENSE                             # License information for the repository

```
---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and share this project with proper attribution.
