import os
import sys
import requests
from google import genai
from dotenv import load_dotenv
from pathlib import Path


# =========================
# LOAD .ENV (LOCAL DEV ONLY)
# =========================
load_dotenv()


# =========================
# HELPERS
# =========================
def get_gemini_api_key() -> str:
    """
    Priority:
    1. Docker secret file (recommended in Docker)
    2. Environment variable (.env or system env)
    """

    # -------------------------
    # 1. Docker secret (preferred)
    # -------------------------
    secret_path = "/run/secrets/gemini_api_key"

    if Path(secret_path).exists():
        key = Path(secret_path).read_text().strip()
        print("[Gemini Key] Loaded from Docker secret")
        return key

    # -------------------------
    # 2. Environment variable fallback
    # -------------------------
    key = os.getenv("GEMINI_API_KEY")

    if key:
        print("[Gemini Key] Loaded from environment variable")
        return key

    raise RuntimeError("Missing Gemini API key (no secret or env found)")


# =========================
# GEMINI
# =========================
def prompt_gemini(model: str, prompt: str) -> str:
    api_key = get_gemini_api_key()

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {repr(e)}")

    if not getattr(response, "candidates", None):
        raise RuntimeError("Gemini returned no candidates")

    candidate = response.candidates[0]

    if candidate.finish_reason and candidate.finish_reason != "STOP":
        raise RuntimeError(f"Gemini blocked response: {candidate.finish_reason}")

    if not candidate.content or not getattr(candidate.content, "parts", None):
        raise RuntimeError("Gemini returned empty content")

    output = "".join(
        part.text for part in candidate.content.parts
        if hasattr(part, "text")
    )

    if not output.strip():
        raise RuntimeError("Gemini returned empty text")

    return output


# =========================
# OLLAMA (DOCKER SAFE)
# =========================
def prompt_ollama(model: str, prompt: str) -> str:
    url = "http://host.docker.internal:11434/api/generate"

    try:
        res = requests.post(
            url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if not res.ok:
            raise RuntimeError(f"Ollama HTTP {res.status_code}: {res.text}")

        data = res.json()
        return data.get("response", "")

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Make sure Ollama is running on your host machine."
        )


# =========================
# ROUTER
# =========================
def prompt_model(model: str, prompt: str) -> dict:
    try:
        if model.startswith("gemini-"):
            response = prompt_gemini(model, prompt)
        else:
            response = prompt_ollama(model, prompt)

        return {
            "success": True,
            "response": response
        }

    except Exception as e:
        print(f"[LLM ERROR - {model}] {repr(e)}")

        return {
            "success": False,
            "error": "LLM service temporarily unavailable. Please try again."
        }


# =========================
# CLI TEST
# =========================
def test_prompt():
    if len(sys.argv) != 3:
        return "Usage: uv run prompt_model.py <model> <prompt>"

    model = sys.argv[1]
    prompt = sys.argv[2]

    return prompt_model(model, prompt)


if __name__ == "__main__":
    print(test_prompt())
