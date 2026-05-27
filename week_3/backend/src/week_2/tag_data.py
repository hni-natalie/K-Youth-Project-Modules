import sqlite3
import logging
import time
from pathlib import Path 
from prompt_model import prompt_model

GREEN = "\033[92m"
RESET = "\033[0m"

# Database Path
DB = Path("data/jobs_d1.db")

# Model
MODEL = "gemini-2.5-flash-lite"

# Logging setup 
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s", # ONLY show the message
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# Batch Config
BATCH_SIZE = 5
RETRY_DELAY = 2
MAX_RETRIES = 3

BATCH_PROMPT = """
You are a machine parser.

You MUST follow these rules exactly:

- Output ONLY raw results
- NO titles
- NO introduction
- NO explanation
- NO headings
- NO markdown
- NO extra text before or after

OUTPUT FORMAT (STRICT):
Each line must be exactly:
<JobID>: <tech1>, <tech2>, <tech3>

HARD RULES:
- Output must start immediately with a JobID
- First character of output must be a digit
- Do NOT output any sentence or label
- Do NOT output "Here is..."
- Do NOT output any preamble
- Do NOT output fewer or more lines than input
- If no technical stack is found, output:
  <JobID>: none

If you break format, output is invalid.

INPUT:
"""


def get_batch(cursor):
    """
        Fetch jobs missing tech_stack
    """

    cursor.execute("""
        SELECT source_id, description
        FROM jobs
        WHERE tech_stack IS NULL OR tech_stack = ''
        LIMIT ?
    """, (BATCH_SIZE,))

    return cursor.fetchall()


def build_prompt(batch):
    """
        Build one batch prompt for LLM
    """
    prompt = BATCH_PROMPT

    for job_id, description in batch:
        prompt += f"""
            Job ID: {job_id}
            Description: 
            {description}
        """

    return prompt

def parse_response(response, batch_size):
    """
        Clean and validate LLM response
        Returns only valid JobID lines
    """

    lines = [
        line.strip()
        for line in response.strip().split("\n")
        if line.strip()
    ]

    # Keep only valid job lines
    valid_lines = []

    for line in lines:
        # must contain ":" and start with a digit
        if ":" in line:
            job_id, tech = line.split(":", 1)
            if job_id.strip().isdigit():
                valid_lines.append(line)

    # Debug
    # print(len(valid_lines))
    # print(valid_lines)

    # Validate
    if len(valid_lines) != batch_size:
        raise ValueError(f"Mismatch: expected {batch_size}, got {len(valid_lines)}")

    return valid_lines


def update_database(cursor, responses):
    """
        Update tech_stack column
    """
    for res in responses:
        # Double check the format 
        if ":" not in res:
            continue

        job_id, tech_stack = res.split(":", 1)

        job_id = job_id.strip()
        tech_stack = tech_stack.strip()

        cursor.execute("""
            UPDATE jobs
            SET tech_stack = ?
            WHERE source_id = ?
        """, (tech_stack, job_id))

        log.info(f"Analyzed Job {GREEN}{job_id}{RESET}: {tech_stack}")  


def tag_data(db_url: str):
    conn = None

    try:
		# Get access from database
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()

        # Clear previous result for different model testing 
        cursor.execute("""
            UPDATE jobs
            SET tech_stack = NULL
        """)
        conn.commit()

        batch_num = 0

        # Main batch loop
        while True:
            batch = get_batch(cursor)

            # No jobs left to process
            if not batch:
                log.info("\n[INFO] All jobs have been processed. Task completed!")
                break

            batch_num += 1
            attempt = 0
            success = False
            log.info(f"\n=== Processing Batch {batch_num} ===")

            while attempt < MAX_RETRIES:
                attempt += 1

                try:
                    # Prompt LLM to extract tech stack 
                    prompt = build_prompt(batch)
                    response = prompt_model(MODEL, prompt)       

                    # Format tech stack from LLM output 
                    responses = parse_response(response, len(batch))

                    # Update db
                    update_database(cursor, responses)

                    # Save changes 
                    conn.commit()
                    success = True
                    break 
                
                except Exception as e:
                    log.error(f"[Batch {batch_num}] Attempt {attempt} failed: {e}")
                    time.sleep(RETRY_DELAY)

            # Stop outer loop if batch failed
            if not success:
                log.error( f"[Batch {batch_num}] Failed after {MAX_RETRIES} attempts")
                break
        
    except Exception as e:
        log.error(f"Fatal error: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    tag_data(DB)