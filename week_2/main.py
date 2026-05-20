import sys
from pathlib import Path 
from src.prompt_model import prompt_model
from src.tag_data import tag_data

DB = Path("data/jobs.db")

def test_prompt():
    if len(sys.argv) != 3:
        print(f'Usage: uv run prompt_model.py <model> <prompt>')
    else:        
        model = sys.argv[1]
        prompt = sys.argv[2]
        prompt_model(model, prompt)


def main():
    tag_data(DB)


if __name__ == "__main__":
    main()
