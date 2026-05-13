import json
import sqlite3

def run_data_profile(db_path):
    # Header
    print('--- 🔍 DATA QUALITY REPORT ---')

    # Get access to the database 
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Calculate total records
    cursor.execute(""" 
        SELECT COUNT(*) FROM jobs
    """)

    total_records = cursor.fetchone()[0]
    print(f'📈 Total Records: {total_records}')

    # Calculate null values in job_title, company, or description 
    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM jobs 
        WHERE job_title is NULL           
    """)
    missing_job_title = cursor.fetchone()[0]

    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM jobs 
        WHERE company is NULL           
    """)
    missing_company = cursor.fetchone()[0]

    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM jobs 
        WHERE description is NULL           
    """)
    missing_desc = cursor.fetchone()[0]
    print(f'❓ Missing Values -> job_title: {missing_job_title}, company: {missing_company}, description: {missing_desc}')

    # Calculate average `description` length
    cursor.execute(""" 
        SELECT AVG(LENGTH(description)) 
        FROM jobs           
    """)
    avg_desc = cursor.fetchone()[0]
    print(f'📝 Avg Description Length: {int(avg_desc)} chars')

    # Find shortest `description` length, along with its `source_id` and `job_title`
    cursor.execute(""" 
        SELECT source_id, job_title, LENGTH(description)
        FROM jobs
        ORDER BY LENGTH(description) ASC
    """)
    shortest_desc = cursor.fetchone()
    print(f'⚠️  Shortest Description: {shortest_desc[2]} chars')
    print(f'    ↳ source_id: {shortest_desc[0]} | job_title: {shortest_desc[1]}')

    # Find longest `description` length, along with its `source_id` and `job_title`
    cursor.execute(""" 
        SELECT source_id, job_title, LENGTH(description)
        FROM jobs
        ORDER BY LENGTH(description) DESC
    """)
    longest_desc = cursor.fetchone()
    print(f'⚠️  Shortest Description: {longest_desc[2]} chars')
    print(f'    ↳ source_id: {longest_desc[0]} | job_title: {longest_desc[1]}')
