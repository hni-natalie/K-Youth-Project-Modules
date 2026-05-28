from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List
import os
import tempfile
from pathlib import Path

from pypdf import PdfReader

from src.week_2.find_skill_gaps import find_skill_gaps
from src.week_2.prompt_model import prompt_model
from src.week_2.tag_data import tag_data

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_URL = BASE_DIR / "week_2" / "data" / "jobs_d1.db"

MODEL = "llama3.1"
# MODEL = "gemini-3-flash-preview"

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
# PDF TEXT EXTRACTION
# =========================
def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text.strip()


# =========================
# CHAT ENDPOINT
# =========================
@app.post("/chat")
async def chat(
    message: str = Form(""),
    files: List[UploadFile] = File(default=[])
):
    temp_file_paths = []

    print("=== REQUEST RECEIVED ===")
    print("Message:", message)
    print("Number of files:", len(files))

    for f in files:
        print("Filename:", f.filename)
        print("Content type:", f.content_type)

    try:
        # =========================
        # Save uploaded files
        # =========================
        for f in files:
            suffix = os.path.splitext(f.filename)[-1]

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(await f.read())
            tmp.close()

            temp_file_paths.append(tmp.name)

        # =========================
        # CASE 1: NO FILE
        # =========================
        if not temp_file_paths:
            result = prompt_model(MODEL, message)

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

        # =========================
        # CASE 2: WITH FILE (PDF → TEXT)
        # =========================
        tag_data(DB_URL)

        pdf_path = temp_file_paths[0]

        # 1. extract text from PDF
        pdf_text = extract_pdf_text(pdf_path)

        # 2. save to txt (debuggable + reusable)
        txt_path = pdf_path.replace(".pdf", ".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(pdf_text)

        # 3. run skill gap analysis on text file
        skill_result = find_skill_gaps(txt_path, DB_URL)

        prompt = f"""
        User message:
        {message}

        Skill Gap Analysis:
        {skill_result}
        """

        result = prompt_model(MODEL, prompt)

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
                "message": "Something went wrong. Please try again."
            }
        )

    finally:
        # =========================
        # Cleanup temp files
        # =========================
        for path in temp_file_paths:
            try:
                os.remove(path)
            except Exception:
                pass
