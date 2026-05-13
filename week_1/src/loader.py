import os
import json
import sqlite3

def load_all_jsons(input_dir, output_dir):
    # Create output folder
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    inserted = 0
    skipped = 0

    # Header
    print("🥇 Gold:...")

    # Create Database 
    db_path = output_dir / "jobs.db"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Create Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT,
            tech_stack TEXT         
        )
    """)

    # Read JSON files
    for json_path in input_dir.glob("*.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cursor.execute(""" 
            INSERT OR IGNORE INTO jobs (
                source_id,
                job_title,
                company,
                description,
                tech_stack
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["source_id"],
            data["job_title"],
            data["company"],
            data["description"],
            ""
        ))

        # Check 
        if cursor.rowcount == 1:
             print(f"✅ Inserted: {json_path.name}")
             inserted += 1
        else:
            print(f"⏭️ Skipped (duplicate): {json_path.name}")
            skipped += 1

        total += 1

    # Save changes 
    connection.commit()
    connection.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")
