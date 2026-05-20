from typing import List
from pathlib import Path 
from pydantic import BaseModel
import sqlite3

RESUME = Path("data/resume_d3.txt")

class SkillGapResult(BaseModel):
    gaps: List[str]



def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    try:

        # Extract technical skill from resume 
        with open(input_file_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        # resume_skills

        # Connect DB
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()




    except Exception as e:
        return SkillGapResult(gaps=[])
