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


## Setup Instructions 

### Prerequisites 
- Python 3.10 or higher
- uv package manager 
- Built-in libraries only (no external API keys / environment variables required for Week 1)


### Install Dependencies 
1. Clone / download the project folder to your local machine
2. Open terminal inside the project root folder
3. Install dependencies using `uv sync`


### Usage 
#### EXTRACTOR
```bash
uv run python main.py ingest
```
Extract data in `data/0_source` from MHTML to HTML and store in `data/1_bronze`

#### Expected Output 
```bash
🥉 Bronze:...
✅ Extracted: Junior Software Engineer (QA & Automation) - JB Job in Johor Bahru, Johor - Jobstreet.mhtml
✅ Extracted: AI Solution Engineer Job in Taman Desa Cemerlang, Johor - Jobstreet.mhtml
✅ Extracted: Graduate Software Engineer _ Developer Job in Kuala Lumpur - Jobstreet.mhtml
...
📊 Bronze Summary:
Total: 100 | Extracted: 100 | Failed: 0
```
---

#### TREATMENT PLANT 
```bash
uv run python main.py process
```
Parses HTML into cleaned JSON saved to `data/2_silver`

#### Expected Output 
```bash
🥈 Silver:...
✅ Processed: Application Developer (Oracle SQL, Python, HTML) Job in Bangsar South, Kuala Lumpur - Jobstreet.html
✅ Processed: Software Developer Job in Petaling, Selangor - Jobstreet.html
✅ Processed: Data Scientist Job in Cyberjaya, Selangor - Jobstreet.html
✅ Processed: IT Application Developer Job in Kelana Jaya, Selangor - Jobstreet.html
...
📊 Silver Summary:
Total: 100 | Processed: 84 | Skipped: 16
```
---

#### BLUEPRINT & THE VAULT
```bash
uv run python main.py load
```
Creates `data/3_gold/jobs.db` to inserts all JSON records from `data/2_silver`

#### Expected Output 
```bash
🥇 Gold:...
✅ Inserted: Software Developer Job 2 in Kuala Lumpur City Centre, Kuala Lumpur - Jobstreet.json
✅ Inserted: EXECUTIVE, SOFTWARE ENGINEER_SOFTWARE DEVELOPMENT Job in Puchong, Selangor - Jobstreet.json
...
📊 Gold Summary:
Total: 84 | Inserted: 84 | Skipped: 0
```
---

#### QA INSPECTOR
```bash
uv run python main.py profile
```
Return data quality metrics (null counts, row counts) based on `data/3_gold/jobs.db` 

#### Expected Output 
```bash
--- 🔍 DATA QUALITY REPORT ---
📈 Total Records: 84
❓ Missing Values -> job_title: 0, company: 0, description: 0
📝 Avg Description Length: 2654 chars
⚠️  Shortest Description: 32 chars
   ↳ source_id: 91647393 | job_title: Software Engineer
🚨 Longest Description: 6781 chars
   ↳ source_id: 91731564 | job_title: Automation Engineer
```
---

#### ORCHESTRATOR 
```bash
uv run python main.py all
```
Run full pipeline 

#### Expected Output 
```text
[output of Extractor]
[output of Treatment Plant]
[output of Blueprint & the vault]
[output of QA Inspector]
```

## Technical Reflections

### Module 1: The Extractor (Medallion & Lakehouses)
Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?
- **Answer**: Keeping the original raw HTML/MHTML files follows industry data lake best practices by preserving an immutable source of truth, rather than only saving processed data directly into a database. Retaining raw files makes debugging far easier because we can re-parse and re-generate cleaned Silver JSON or rebuild the Gold database at any time if parsing logic, schema design, or transformation rules need to be fixed or updated. It also provides full data recoverability; if downstream structured data becomes corrupted or duplicated, we can always reset the pipeline and reprocess from the untouched raw source without needing to re-scrape the website again.

### Module 2: Treatment Plant (ETL vs ELT & Scale)
Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?
- **Answer**: Cloud data platforms follow the ELT (Extract, Load, Transform) model instead of traditional ETL because they first ingest and store raw unprocessed data into the data lake immediately, before any cleaning or transformation. Loading raw data first is faster, scalable, and avoids blocking ingestion by heavy cleaning logic upfront. Processing files one by one sequentially is slow and bottlenecked, especially with large datasets. If one file fails parsing or has a malformed format, the whole pipeline can stall, and errors are harder to trace in a linear workflow. Distributed processing splits raw files across multiple servers to process them in parallel instead of one at a time. It drastically speeds up pipeline execution, isolates failures so one bad file does not break the whole workflow, and scales easily as more raw data is added.

### Module 3: The Blueprint & The Vault (Storage & Contracts)
What should happen if an important field like job_title disappears? Why fail early instead of silently inserting nulls into DB? How does INSERT OR IGNORE help prevent duplicate records?
- **Answer**: If job_title is missing from the JSON (e.g., data['job_title'] does not exist), Python will immediately throw a KeyError and crash the pipeline. This happens before the SQL insert even runs — the script cannot find the value to pass into the ? placeholder. Failing early is a critical industry best practice because prevents bad/incomplete data from entering the Gold database and make debugging fast and obvious. INSERT OR IGNORE uses the primary key source_id to check for duplicates. If the source_id already exists in the database, skip insertion and makes the pipeline idempotent (safe to re-run).

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)
- **Answer**: If `processor.py` crashes halfway through execution, the pipeline typically ends up in a partaily completed state: some files may already be processed and saved, while others remain unprocessed, and there is usually no built-in record of exactly where it stopped. This means I either have to rerun the entire pipeline or manually inspect and resume from where it failed, which is error-prone and inefficient. In contrast, orchestration tools like Apache Airflow are more reliable because they ley us define our pipeline as a Directed Acyclic Graph, where each node is a task and arrows define dependencies. Hence, they allow pipelines to resume from the exact point of failure instead of restarting from scratch. As a result, unlike manual Python scripts that rely on ad-hoc error handling, orchestrators provide fault tolerance, observability, and recoverability out of the box. 
