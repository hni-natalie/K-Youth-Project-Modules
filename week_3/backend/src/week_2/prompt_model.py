import os
import sys
import requests
from google import genai
from dotenv import load_dotenv


# =========================
# GEMINI
# =========================
def prompt_gemini(model: str, prompt: str) -> str:
    """
    Handle Gemini model requests safely
    """
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

    except Exception as e:
        # catches 404, 503, quota, invalid model, etc.
        raise RuntimeError(f"Gemini API error: {repr(e)}")

    # =========================
    # Validate response object
    # =========================
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
# OLLAMA
# =========================
def prompt_ollama(model: str, prompt: str) -> str:
    """
    Handle Ollama model requests safely (Docker-safe)
    """

    OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

    try:
        res = requests.post(
            OLLAMA_URL,
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
            "Make sure Ollama is running on host machine."
        )

# =========================
# ROUTER
# =========================
def prompt_model(model: str, prompt: str) -> dict:
    """
    Route request to correct model provider
    Returns structured response for FastAPI
    """

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
        # backend debug only (never expose raw error to frontend)
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
