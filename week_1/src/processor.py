from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError
import json

# Pydantic Model 
class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

def process_all_html(input_dir, output_dir):
    # Create output folder
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    processed = 0
    skipped = 0

    print("🥈 Silver:...")

    # Loop all HTML files
    for html_file in input_dir.glob("*.html"):
        total += 1

        try:
            # Read HTML with utf-8
            html = html_file.read_text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")

            # Extract unique_id (source_id) from og:url
            og_url = soup.find("meta", property="og:url")
            if not og_url:
                print(f"⚠️ Missing source_id (og:url) in: {html_file.name}")
                skipped += 1
                continue

            url = og_url["content"]
            source_id = url.strip("/").split("/")[-1]

            # Extract Job Title, Company, Description 
            title_tag = soup.find(attrs={"data-automation": "job-detail-title"})
            company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
            description_tag = soup.find(attrs={"data-automation": "jobAdDetails"})

            job_title = title_tag.get_text(separator=" ", strip=True) if title_tag else ""
            company = company_tag.get_text(separator=" ", strip=True) if company_tag else ""
            description = description_tag.get_text(separator=" ", strip=True) if description_tag else ""

            # Skip incomplete records 
            missing = []
            if not job_title:
                missing.append("job_title")

            if not company:
                missing.append("company")

            if not description:
                missing.append("description")

            if missing:
                print(f"⚠️ Missing {', '.join(missing)} in: {html_file.name}")
                skipped += 1
                continue

            # Validate
            job = JobListing(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description
            )    

            # Save JSON
            json_path = output_dir / f"{html_file.stem}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(job.model_dump(), f, ensure_ascii=False, indent=4)

            print(f"✅ Processed: {html_file.name}")
            processed += 1
        
        except Exception as e:
            print(f"⚠️ Error: {e} | Error processing: {html_file.name}")
            skipped +=1

    # Summary
    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")