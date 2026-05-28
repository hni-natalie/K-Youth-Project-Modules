from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List
from pathlib import Path

from src.week_2.find_skill_gaps import find_skill_gaps
from src.week_2.prompt_model import prompt_model
from src.week_2.tag_data import tag_data

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_URL = BASE_DIR / "week_2" / "data" / "jobs_d1.db"

MODEL = "gemini-2.5-flash"

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def health_check():
    return {"status": "ok"}


# =========================
# SKILL GAP DETECTOR
# =========================
def wants_skill_gap_analysis(message: str) -> bool:
    if not message:
        return False

    message = message.lower()

    keywords = [
        "skill gap", "skills gap", "missing skill", "missing skills",
        "gap analysis", "analyze resume", "analyse resume",
        "resume analysis", "cv analysis", "improve my resume",
        "what skills am i missing", "what am i missing",
        "match my resume"
    ]

    return any(k in message for k in keywords)


# =========================
# CHAT ENDPOINT
# =========================
@app.post("/chat")
async def chat(
    message: str = Form(""),
    pdf_text: str = Form(""),
    files: List[UploadFile] = File(default=[])
):

    print("\n=== REQUEST RECEIVED ===")
    print("Message:", repr(message))
    print("Files:", len(files))
    print("PDF text length:", len(pdf_text))

    # =========================
    # BASIC INPUT VALIDATION
    # =========================
    has_message = bool(message and message.strip())
    has_resume = bool(files and pdf_text and pdf_text.strip())

    if not has_message and not has_resume:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Please provide a message or upload a resume."
            }
        )

    try:

        wants_skill_gap = wants_skill_gap_analysis(message)

        # =========================
        # CASE 1: Resume + Skill Gap
        # =========================
        if has_resume and wants_skill_gap:

            print("CASE 1: Resume + Skill Gap")

            # avoid running DB tagging every request (optional optimization)
            tag_data(DB_URL)

            skill_result = find_skill_gaps(pdf_text, DB_URL)

            prompt = f"""
You are a resume assistant.

User Message:
{message}

Resume:
{pdf_text}

Skill Gap Analysis:
{skill_result}

Task:
Use the resume + skill gap analysis to answer the user clearly.
"""

            result = prompt_model(MODEL, prompt)

        # =========================
        # CASE 2: Resume Only
        # =========================
        elif has_resume:

            print("CASE 2: Resume only")

            prompt = f"""
You are a resume assistant.

User Message:
{message}

Resume:
{pdf_text}

Task:
Answer only using the resume content.
"""

            result = prompt_model(MODEL, prompt)

        # =========================
        # CASE 3: Normal Chat
        # =========================
        else:

            print("CASE 3: Prompt only")

            # extra safety: prevent empty prompt to LLM
            if not has_message:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "Empty message is not allowed."
                    }
                )

            result = prompt_model(MODEL, message)

        # =========================
        # LLM FAILURE HANDLING
        # =========================
        if not result.get("success"):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": result.get("error", "LLM failed")
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "response": result["response"]
            }
        )

    except Exception as e:
        print(f"[CHAT ERROR] {repr(e)}")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error"
            }
        )
