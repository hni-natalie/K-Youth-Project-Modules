from pathlib import Path 
import email
import quopri 

def ingest_all_mhtml(input_dir, output_dir):
    # Create otuptu folder if it doesn't exist 
    output_dir.mkdir(parents=True, exist_ok=True)

    total_files = 0
    extracted = 0
    failed = 0

    # Header print
    print("🥉 Bronze: Extractor ")

    # Loop through all .mhtml files in source folder
    for mhtml_file in input_dir.glob("*.mhtml"):
        total_files += 1

        try: 
            # Read the MHTML file as bytes (like an email)
            file_content = mhtml_file.read_bytes()

            # Parse MHTML as an email message 
            msg = email.message_from_bytes(file_content)

            html_content = None

            # Find the part that is text/html
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    # De# Decode the quoted-printable encoding
                    encoded_html_content = part.get_payload()
                    decoded_bytes = quopri.decodestring(encoded_html_content)
                    html_content = decoded_bytes.decode("utf-8", errors="ignore")
                    break

            # If NO HTML found → show warning
            if not html_content or html_content.strip() == "":
                print(f"⚠️ No HTML content found in: {mhtml_file.name}")
                failed += 1
                continue

            # Save as .html to 1_bronze
            html_filename = mhtml_file.stem + ".html"
            output_file = output_dir / html_filename
            output_file.write_text(html_content, encoding="utf-8")

            # Success message
            print(f"✅ Extracted: {mhtml_file.name}")
            extracted += 1

        except Exception as e:
            # Any error, we mark as failed 
            print(f"⚠️ No HTML content found in: {mhtml_file.name}")
            failed += 1

    # Print summary
    print("\n📊 Bronze Summary:")
    print(f"Total: {total_files} | Extracted: {extracted} | Failed: {failed}")
