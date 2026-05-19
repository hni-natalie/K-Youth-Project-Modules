import sys
import os
import requests
from google import genai

def prompt_model(model: str, prompt: str) -> str :
    
    print("\n--- RESPONSE ---\n")

    # Gemini Model
    if model.startswith("gemini-"):
        try:
            API_KEY = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=API_KEY)

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(response.text)

        except Exception as e:
            print(f"[Gemini Error] {str(e)}")
            
    # Ollama Model
    else:
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

            # Check for error first
            if "error" in data:
                print(f"[Ollama Error] {data['error']}")
                return

            # Safe access
            print(data.get("response", "[No response field returned]"))
        except Exception as e:
            print(f"[Ollama Error] {str(e)}")
        

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: uv run prompt_model.py <model> <prompt>')
    else:        
        model = sys.argv[1]
        prompt = sys.argv[2]
        prompt_model(model, prompt)