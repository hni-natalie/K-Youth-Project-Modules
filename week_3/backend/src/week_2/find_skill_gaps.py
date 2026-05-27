from typing import List
from pathlib import Path 
import sqlite3
from pydantic import BaseModel
from prompt_model import prompt_model

GREEN = "\033[92m"
RESET = "\033[0m"

DB = Path("data/jobs_d1.db")
RESUME = Path("data/resume_d3.txt")

MODEL = "gemini-2.5-flash-lite"

PROMPT = """
You are a strict machine parser with fixed output rules.

You MUST follow these rules exactly:

RULES:
- Extract ONLY technical skills.
- Ignore certifications.
- Ignore languages.
- Ignore soft skills.
- Ignore education.
- Ignore achievements.
- Ignore hobbies.
- Ignore non-technical skills.
- Convert everything to lowercase.
- Preserve exact technical skill names.
- Do NOT split combined skills incorrectly.
  Example:
  - "C/C++" must remain "c/c++"
  - "C++" must remain "c++"

OUTPUT FORMAT:
Return ONLY a comma-separated list of technical skills.

NO:
- explanations
- markdown
- headings
- extra text
- bullet points

RESUME:
"""

class SkillGapResult(BaseModel):
    # List of missing skills 
    gaps: List[str]


def normalize_skills(skill_text: str) -> set:
    """
        Normalize skill names for deterministic matching
    """
    skills = set()

    if not skill_text:
        return skills

    for skill in skill_text.split(","):
        skill = skill.strip().lower()

        if not skill:
            continue

        # C variants
        if skill in {
            "c",
            "c++",
            "c/c++",
            "cpp",
            "c ++"
        }:
            skill = "c/c++"

        # JavaScript variants
        elif skill in {
            "javascript",
            "js"
        }:
            skill = "javascript"

        # TypeScript variants
        elif skill in {
            "typescript",
            "ts"
        }:
            skill = "typescript"

        # Node.js variants
        elif skill in {
            "node",
            "nodejs",
            "node.js"
        }:
            skill = "node.js"

        # Power BI naming
        elif skill in {
            "powerbi",
            "power bi"
        }:
            skill = "power bi"

        # SQL naming
        elif skill == "mysql database":
            skill = "mysql"

        elif skill == "postgres":
            skill = "postgresql"

        # Cloud naming
        elif skill == "amazon web services":
            skill = "aws"

        elif skill in {
            "google cloud",
            "google cloud platform"
        }:
            skill = "gcp"

        # LLM naming
        elif skill in {
            "llms",
            "large language models"
        }:
            skill = "llm"

        # CI/CD naming
        elif skill in {
            "continuous integration",
            "continuous delivery"
        }:
            skill = "ci/cd"

        skills.add(skill)

    return skills


def get_resume_skills(input_file_path: str) -> set[str]:
    """
        Extract technical skills from resume using LLM
    """
    with open(input_file_path, "r", encoding="utf-8") as f:
        resume_text = f.read()

    prompt = PROMPT + resume_text
    response = prompt_model(MODEL, prompt)

    # Handle model errors returned as text
    if not response:
        raise RuntimeError("Empty response from model")

    response_lower = response.lower()

    if (
        "gemini error" in response_lower
        or "ollama error" in response_lower
        or "no api key" in response_lower
    ):
        raise RuntimeError(response)

    return normalize_skills(response)


def get_job_skills(db_url: str, batch_size: int = 500) -> set[str]:
    job_skills = set()

    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    last_id = 0

    while True:
        cursor.execute("""
            SELECT source_id, tech_stack
            FROM jobs
            WHERE tech_stack IS NOT NULL
            AND tech_stack != 'none'
            AND source_id > ?
            ORDER BY source_id
            LIMIT ?
        """, (last_id, batch_size))

        rows = cursor.fetchall()

        if not rows:
            break

        for job_id, tech_stack in rows:
            last_id = job_id
            job_skills.update(normalize_skills(tech_stack))

    conn.close()
    return job_skills


def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    try:
        # Prompt LLM to extract technical skill
        resume_skills = get_resume_skills(input_file_path)
        print(f'Resume_skills: \n{resume_skills}\n') # debug

        # Extract job_skills from database
        job_skills = get_job_skills(db_url)
        print(f'Job skills: \n{job_skills}\n') # debug

        gaps = sorted(job_skills - resume_skills)
        return SkillGapResult(gaps=gaps)

    except Exception as e:
        print(f"Job skill extraction failed: {e}")
        return SkillGapResult(gaps=[])


if __name__ == "__main__":
    result = find_skill_gaps(RESUME, DB)
    print(f"{GREEN}{result}{RESET}")
