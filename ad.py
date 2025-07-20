import os
import pandas as pd
from database import problems_collection

# --- CONFIG ---
BASE_FOLDER = r"D:\leetcode-company-wise-problems"
CSV_FILENAME = "5. All.csv"

def clean_topics(topics_str):
    """Converts comma-separated topics string to a clean list."""
    print(f"🔧 Cleaning topics from: {topics_str}")
    return [topic.strip() for topic in topics_str.split(",") if topic.strip()]

def upload_all_csvs(base_path):
    print(f"🚀 Starting upload from base folder: {base_path}")
    
    total_uploaded = 0
    total_skipped = 0
    total_companies = 0

    if not os.path.isdir(base_path):
        print(f"❌ Base folder does not exist: {base_path}")
        return

    for company in os.listdir(base_path):
        company_path = os.path.join(base_path, company)
        csv_path = os.path.join(company_path, CSV_FILENAME)

        if not os.path.isdir(company_path):
            print(f"📁 Skipping non-directory: {company_path}")
            continue

        total_companies += 1
        print(f"\n📂 Company: {company}")
        print(f"🔎 Looking for CSV at: {csv_path}")

        if not os.path.isfile(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            continue

        try:
            print("📥 Reading CSV...")
            df = pd.read_csv(csv_path)
            print(f"📄 Loaded {len(df)} rows.")
            df.fillna("", inplace=True)

            for idx, row in df.iterrows():
                print(f"\n➡️ Processing row {idx + 1}...")

                title = row.get("Title", "").strip()
                link = row.get("Link", "").strip()

                if not title or not link:
                    print("⚠️ Skipping: Missing title or link.")
                    total_skipped += 1
                    continue

                difficulty = row.get("Difficulty", "").strip().upper()
                frequency = float(row.get("Frequency", 0))
                acceptance_rate = float(row.get("Acceptance Rate", 0))
                topics_str = row.get("Topics", "")

                print(f"📌 Title: {title}")
                print(f"🔗 Link: {link}")
                print(f"📊 Difficulty: {difficulty}, Frequency: {frequency}, Acceptance: {acceptance_rate}")
                print(f"🏷️ Topics Raw: {topics_str}")

                topics = clean_topics(topics_str)

                problem_data = {
                    "company": company,
                    "difficulty": difficulty,
                    "title": title,
                    "frequency": frequency,
                    "acceptance_rate": acceptance_rate,
                    "link": link,
                    "topics": topics,
                    "company_tag": [company],
                }

                print("🔎 Checking for existing entry in database...")
                existing = problems_collection.find_one({"link": link})

                if existing:
                    print("♻️ Entry exists.")
                    if company not in existing.get("company_tag", []):
                        print(f"➕ Adding company '{company}' to existing entry.")
                        problems_collection.update_one(
                            {"_id": existing["_id"]},
                            {"$addToSet": {"company_tag": company}}
                        )
                    else:
                        print("⚠️ Company already tagged. Skipping.")
                        total_skipped += 1
                        continue
                else:
                    print("✅ New entry. Inserting to database.")
                    problems_collection.insert_one(problem_data)
                    total_uploaded += 1

        except Exception as e:
            print(f"❌ Error processing {company}: {e}")

    print("\n🚧 Upload complete.")
    print(f"📦 Companies processed: {total_companies}")
    print(f"✅ Problems uploaded: {total_uploaded}")
    print(f"⏭️ Problems skipped: {total_skipped}")

# --- MAIN ---
if __name__ == "__main__":
    upload_all_csvs(BASE_FOLDER)
