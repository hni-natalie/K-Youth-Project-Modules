# Week 2 - AI Component

## 📌 Project Overview
This project uses Large Language Models (LLMs) to improve job–candidate skill matching through data tagging and skill gap analysis. Job descriptions stored in a SQLite database are processed to extract and tag technical skills into a structured tech_stack column, transforming unstructured text into machine-readable features. Candidate resumes are then analyzed to extract only relevant technical skills while ignoring certifications, soft skills, and non-technical information. A normalization process standardizes skill variations (e.g., js → javascript, nodejs → node.js) to improve matching accuracy and determinism. Finally, the system compares resume skills against job technology stacks to identify missing technical competencies, demonstrating the use of LLM-based feature engineering, structured input/output handling, and reliable skill extraction for better predictions.

## 🚀 Setup Instructions

Follow the steps below to set up and run the project locally.

### 📋 Prerequisites

Ensure you have the following installed:

- **Python 3.10+**
- **uv** (Python package manager)
- SQLite (usually included with Python)

Check your Python version:

```bash
python --version
```

---

### 📦 Install `uv`

If `uv` is not installed, install it using:

#### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```bash
uv --version
```

---

### 📁 Clone the Repository

```bash
git clone <your-repository-url>
cd <project-folder>
cd week_2
```

---

### 🛠️ Create Virtual Environment

Create and activate a virtual environment:

```bash
uv venv
```

Activate the environment:

#### macOS / Linux
```bash
source .venv/bin/activate
```

#### Windows
```bash
.venv\Scripts\activate
```

---

### 📚 Install Dependencies

Install all required packages:

```bash
uv sync
```

---

### 🔐 Configure Environment Variables

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key.

⚠️ **Do not commit API keys or secrets to version control.**

---

### 🗂️ Project Structure

Ensure the following files exist:

```text
data/
├── jobs_d1.db
├── jobs.db
├── resume_d3.txt
├── rate_limits.txt
├── pyproject.toml
├── uv.lock
└── README.md

find_skill_gaps.py
tag_data.py
prompt_model.py
```

---

### ▶️ Running the Project

Run model prompt:

```bash
uv run prompt_model.py <model> <prompt>
```

Run job data tagging:

```bash
uv run tag_data.py
```

Run skill gap analysis:

```bash
uv run find_skill_gaps.py
```

---

### ✅ Expected Outcome

The system will:

- Extract technical skills from resumes 📄
- Tag technical stacks from job descriptions 🏷️
- Compare skills and identify missing competencies 🔍
- Return normalized and deterministic skill gaps 📊

---

## 🧩 API / Function Reference

This project consists of three main modules:

- `tag_data.py` → Extracts and tags technical skills from job descriptions.
- `find_skill_gaps.py` → Compares resume skills against job requirements.
- `prompt_model.py` → Handles LLM prompting and response generation.

---

## 📌 `tag_data.py`

### `tag_data(db_url: str)`

**Purpose**  
Reads job descriptions from the `jobs` table and populates the `tech_stack` column with extracted technical skills using an LLM.

**Inputs**

| Parameter | Type | Description |
|---|---:|---|
| `db_url` | `str` | Path to the SQLite database |

**Expected Format**

```python
tag_data("data/jobs_d1.db")
```

**Output**

- Updates the `tech_stack` column in the `jobs` table.
- Stores comma-separated technical skills.

Example:

```text
python, docker, aws, mysql
```

---

## 📌 `find_skill_gaps.py`

### `find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult`

**Purpose**  
Extracts technical skills from a resume and compares them against the job technology stack to identify missing skills.

**Inputs**

| Parameter | Type | Description |
|---|---:|---|
| `input_file_path` | `str` | Path to the resume text file |
| `db_url` | `str` | Path to the SQLite database |

**Expected Format**

```python
find_skill_gaps(
    "data/resume_d3.txt",
    "data/jobs_d1.db"
)
```

**Output**

Returns a `SkillGapResult` object.

Structure:

```python
class SkillGapResult(BaseModel):
    gaps: List[str]
```

Example:

```python
SkillGapResult(
    gaps=['aws', 'docker', 'java']
)
```

---

## 📌 `prompt_model.py`

### `prompt_model(model: str, prompt: str) -> str`

**Purpose**  
Sends prompts to an LLM and returns generated responses for technical skill extraction.

**Inputs**

| Parameter | Type | Description |
|---|---:|---|
| `model` | `str` | Name of the LLM model |
| `prompt` | `str` | Prompt text sent to the model |

Example:

```python
prompt_model(
    "llama3.1:latest",
    prompt
)
```

**Output**

Returns raw model response as a string.

Example:

```text
python, mysql, docker
```

---

## 🔄 Module Interaction Flow

The modules interact in the following order:

```text
Resume.txt
    ↓
find_skill_gaps.py
    ↓
prompt_model.py (LLM extraction)
    ↓
jobs_d1.db (tech_stack)
    ↓
Skill Gap Comparison
    ↓
SkillGapResult(gaps=[...])
```

```text
jobs.db (job description)
    ↓
tag_data.py
    ↓
prompt_model.py (LLM extraction)
    ↓
jobs_d1.db (tech_stack)
```

---

## 📊 Data / Assumptions

### Data Sources

The system uses the following data sources:

#### 1. SQLite Database (`jobs_d1.db`)
The database contains a `jobs` table used for job skill extraction and comparison.

Expected relevant schema:

| Column | Purpose |
|---|---|
| `source_id` | Job Unique ID |
| `description` | Raw job description text |
| `tech_stack` | Extracted technical skills (comma-separated) |

The `tech_stack` column is populated during the data tagging phase (`tag_data.py`) using LLM-based extraction.

Example:

```text
python, docker, aws, mysql
```

---

#### 2. Resume File (`resume_d3.txt`)

The system accepts a plain text resume file as input.

Example structure:

```text
SKILLS
Technical Skills: Python, SQL, Azure, Docker
```

The resume is processed using an LLM to extract only technical skills.

---

### Assumptions

The project makes the following assumptions:

- Resumes are provided in **plain text format (`.txt`)**.
- Technical skills are explicitly mentioned in the resume content.
- The `jobs` table exists in the SQLite database.
- Job descriptions have already been tagged into the `tech_stack` column.
- Certifications, soft skills, hobbies, and languages are ignored.
- Skill names may vary and are normalized to improve matching consistency.

---

### Data Limitations

- LLM extraction quality depends on resume clarity and job description quality.
- Only technical skills are considered; domain knowledge and certifications are excluded.
- Skill matching is based on normalized keyword comparison and does not infer equivalent expertise across unrelated technologies.

---

### Data Flow

The system processes data in the following sequence:

```text
resume.txt
    ↓
LLM Skill Extraction
    ↓
Skill Normalization
    ↓
Resume Skill Set
                    jobs_d1.db
                         ↓
                  tech_stack column
                         ↓
                 Skill Normalization
                         ↓
                    Job Skill Set
                         ↓
               Skill Gap Comparison
                         ↓
                SkillGapResult(gaps)
```

---

## 🧪 Testing

### Testing Approach

The system was tested using multiple resume and database scenarios to validate skill extraction accuracy, normalization behavior, and deterministic outputs.

---

### Test Cases

#### ✅ Resume Skill Extraction

**Input Resume**

```text
Technical Skills: C, C++, Azure, Python, MYSQL
```

**Expected Output**

```python
{
    "c/c++",
    "azure",
    "python",
    "mysql"
}
```

Validation:
- Lowercase conversion
- Correct normalization (`C/C++`)
- Non-technical information excluded

---

#### ✅ Skill Gap Detection

**Resume Skills**

```text
python, mysql, azure
```

**Job Skills**

```text
python, docker, aws, mysql
```

**Expected Gaps**

```python
['aws', 'docker']
```

Validation:
- Correct set comparison
- Alphabetically sorted output

---

#### ✅ Invalid / Empty Data Handling

Scenarios tested:

- Empty resume file
- Missing database values
- `NULL` or `none` values in `tech_stack`
- Invalid database paths

Expected behavior:

```python
SkillGapResult(gaps=[])
```

Validation:
- No crashes
- Graceful error handling

---

### Reliability and Determinism

To ensure correctness and deterministic behavior:

- Strict LLM prompts were used to constrain output format.
- Skills are normalized before comparison.
- Outputs are converted to lowercase.
- Results are sorted alphabetically for consistent ordering.
- Error handling prevents crashes and unexpected failures.

This ensures repeated runs produce consistent and reliable results.

---

## ⚠️ Limitations

### LLM Extraction Accuracy
The quality of extracted skills depends on the language model’s interpretation of resumes and job descriptions. While strict prompts and normalization improve consistency, occasional misclassification or omission of technical skills may still occur, especially for ambiguous terminology or uncommon technologies.

### Resume Format Dependency
The system assumes resumes are provided in plain text (`.txt`) format and contain clearly stated technical skills. Poorly formatted resumes, unconventional layouts, or missing skill sections may reduce extraction accuracy.

### Limited Skill Semantics
Skill matching is primarily based on normalized keyword comparison rather than semantic understanding. For example, related technologies are treated as separate skills (`SQL` vs `MySQL`, `Docker` vs `Kubernetes`) even if practical experience may overlap.

### Scalability Constraints
The use of LLMs introduces additional processing overhead compared to rule-based extraction. Large datasets or frequent API requests may experience slower execution and rate-limiting constraints depending on the selected model provider.

### Incomplete Technical Mapping
Normalization currently covers common aliases and naming variations (e.g., `nodejs → node.js`, `js → javascript`), but may not capture all possible industry naming conventions or synonymous tools.

---

## 🏗️ Architecture Reflection

### Design Choices

The system was designed with modularity and separation of concerns in mind to improve maintainability and debugging. Core responsibilities were divided into dedicated functions, such as resume skill extraction, job skill retrieval, normalization, and skill gap comparison. This structure makes the system easier to extend and test independently. 

### Trade-offs

A key trade-off was prioritizing simplicity and determinism over advanced semantic matching. Rather than building a complex recommendation or embedding-based similarity system, the project uses normalized keyword comparison to ensure reproducible outputs and predictable behavior. While this approach may miss deeper relationships between related technologies, it improves reliability and satisfies deterministic requirements.

### Improvements

A predefined technical skill taxonomy could improve normalization and reduce inconsistent naming. Semantic similarity methods or embeddings could also improve skill matching by recognizing related technologies instead of exact normalized matches. Additionally, batching and caching mechanisms could reduce repeated LLM calls and improve performance for larger databases. Support for additional resume formats such as PDF or DOCX could further improve usability.
