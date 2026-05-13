# Week 1 - Data Input & Processing Component

## 📌 Project Overview
This project is a local ETL (Extract, Transform, Load) data pipeline that processes raw job listing data from the `0_source` directory into a clean, structured SQLite database (`jobs.db`). It extracts messy input data, cleans and standardises the content (especially job descriptions), and loads it into a relational schema for downstream use.

The final output is a fully automated CLI tool (`main.py`) that orchestrates the entire pipeline end-to-end, ensuring the database is consistent, readable, and analysis-ready.

```text
[SOURCE] → [EXTRACT] → [CLEAN / TRANSFORM] → [LOAD] → [DATABASE]
```


The resulting database contains structured job listings with the following schema:

```text
source_id | job_title | company | description | tech_stack
```