import os
import requests
from google import genai


def prompt_gemini(model: str, prompt: str) -> str:
    """
        Handle Gemini model requests
    """
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"[Gemini Error] {str(e)}"


def prompt_ollama(model: str, prompt: str) -> str:
    """
        Handle Ollama model requests
    """

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )

        data = res.json()

        if "error" in data:
            return f"[Ollama Error] {data['error']}"

        return data.get("response", "[No response field returned]")

    except Exception as e:
        return f"[Ollama Error] {str(e)}"


def prompt_model(model: str, prompt: str) -> str:
    """
        Route request to the correct model provider
    """
        
    if model.startswith("gemini-"):
        return prompt_gemini(model, prompt)
    
    return prompt_ollama(model, prompt)