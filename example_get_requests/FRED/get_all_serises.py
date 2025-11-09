import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# --- Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY_FRED")

if not API_KEY:
    raise ValueError("❌ API_KEY_FRED not found in .env file")

BASE_URL = "https://api.stlouisfed.org/fred"
OUTPUT_CSV = "fred_all_series.csv"

# --- Config
DELAY = 0.5          # seconds between requests
MAX_RETRIES = 5      # retry attempts on failure
SAVE_EVERY = 10_000  # save intermediate results after this many series


# --- Core request helper
def fred_request(endpoint, params):
    """Perform GET request with retries and rate limit handling."""
    params["api_key"] = API_KEY
    params["file_type"] = "json"

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
            if r.status_code == 429:  # Rate limit
                wait = (attempt + 1) * 2
                print(f"⚠️  Rate limit hit. Waiting {wait}s...")
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
            time.sleep((attempt + 1) * 2)

    print("❌ Max retries reached. Skipping request.")
    return None


# --- Recursive crawler
def crawl_category(category_id=0, collected=None):
    """Recursively crawl all categories and series."""
    if collected is None:
        collected = []

    # Get all series under this category
    data = fred_request("category/series", {"category_id": category_id})
    if data and "seriess" in data:
        collected.extend(data["seriess"])
        print(f"📦 Category {category_id}: +{len(data['seriess'])} series (total {len(collected)})")

        # Save partial data to CSV periodically
        if len(collected) % SAVE_EVERY < 100:
            df = pd.DataFrame(collected)
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"💾 Intermediate save: {len(collected)} total series.")

    # Explore subcategories
    children = fred_request("category/children", {"category_id": category_id})
    if children and "categories" in children:
        for child in children["categories"]:
            child_id = child["id"]
            child_name = child["name"]
            print(f"➡️  Entering subcategory {child_id}: {child_name}")
            time.sleep(DELAY)
            crawl_category(child_id, collected)

    time.sleep(DELAY)
    return collected


if __name__ == "__main__":
    print("🔄 Starting full FRED crawl from root category (0)...")
    all_series = crawl_category(0)

    df = pd.DataFrame(all_series)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Done! Saved {len(df)} total series to {OUTPUT_CSV}")
