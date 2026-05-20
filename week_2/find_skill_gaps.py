from typing import List
from pathlib import Path 
import sqlite3
from pydantic import BaseModel
from prompt_model import prompt_model

GREEN = "\033[92m"
RESET = "\033[0m"

DB = Path("data/jobs_d1.db")
RESUME = Path("data/resume_d3.txt")

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
    response = prompt_model("llama3.1:latest", prompt)

    return normalize_skills(response)



def get_job_skills(db_url: str) -> set[str]:
    """
        Extract all skills from tech_stack column
    """
    job_skills = set()

    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tech_stack
        FROM jobs
        WHERE tech_stack IS NOT NULL
        AND tech_stack != 'none'
    """)

    rows = cursor.fetchall()

    for row in rows:
        tech_stack = row[0]

        if tech_stack:
            job_skills.update(normalize_skills(tech_stack))

    conn.close()

    return job_skills


def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    try:
        # Extract resume content
        with open(input_file_path, "r", encoding="utf-8") as f:
            resume_content = f.read()

        # Prompt LLM to extract technical skill
        resume_skills = get_resume_skills(input_file_path)
        # print(f'Resume_skills: {resume_skills}') # debug

        # Extract job_skills from database
        job_skills = get_job_skills(db_url)
        # print(f'Job skills: {job_skills}') # debug

        gaps = sorted(job_skills - resume_skills)
        return SkillGapResult(gaps=gaps)

    except Exception:
        return SkillGapResult(gaps=[])


if __name__ == "__main__":
    result = find_skill_gaps(RESUME, DB)
    print(f"{GREEN}{result}{RESET}")
