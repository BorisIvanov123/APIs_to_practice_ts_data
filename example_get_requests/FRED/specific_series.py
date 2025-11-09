import os
import time
import requests
import pandas as pd
import json
from dotenv import load_dotenv
from pathlib import Path

# ============================
# USER SETTINGS (Edit here)
# ============================
SERIES_ID = "GDP"           # Example: GDP, DGS10, CPIAUCSL
START = None                # Set to None to fetch from the earliest available date. If you want a specific date, use "YYYY-MM-DD"
END = None                  # Set to None to fetch up to the latest available date. If you want a specific date, use "YYYY-MM-DD"
# ============================

# --- Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY_FRED")

if not API_KEY:
    raise ValueError("❌ API_KEY_FRED not found in .env file")

# --- Base URLs
BASE_URL_OBS = "https://api.stlouisfed.org/fred/series/observations"
BASE_URL_META = "https://api.stlouisfed.org/fred/series"

# --- Config
DELAY = 1.0        # seconds between requests
MAX_RETRIES = 5     # for network/rate limit recovery
OUTPUT_DIR = Path("data/FRED")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fred_request(url, params):
    """Generic FRED API request helper with retry logic and polite delay."""
    params["api_key"] = API_KEY
    params["file_type"] = "json"

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, timeout=30)
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
    print("❌ Max retries reached.")
    return None


def get_series_metadata(series_id):
    """Fetch metadata for a FRED series (frequency, units, etc.)."""
    data = fred_request(BASE_URL_META, {"series_id": series_id})
    if not data or "seriess" not in data:
        print(f"❌ Invalid or missing series ID: {series_id}")
        return None

    meta = data["seriess"][0]
    print(f"ℹ️  Found series '{series_id}': {meta.get('title')}")
    print(f"   Frequency: {meta.get('frequency')} | Units: {meta.get('units')}")
    return meta


def fetch_series_data(series_id, start_date=None, end_date=None):
    """Fetch time series observations for a valid FRED series."""
    params = {"series_id": series_id}
    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date

    if not start_date and not end_date:
        print("📅 No date range provided — fetching full available dataset...")

    print(f"🔄 Fetching data for '{series_id}' ...")
    data = fred_request(BASE_URL_OBS, params)
    if not data or "observations" not in data:
        print("❌ No observations found.")
        return pd.DataFrame()

    df = pd.DataFrame(data["observations"])
    if df.empty:
        print("⚠️  No data points returned.")
        return df

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    df = df[["date", "value"]]  # Clean layout
    print(f"✅ Retrieved {len(df)} data points.")
    time.sleep(DELAY)
    return df


def save_series(df, meta, series_id, start_date=None, end_date=None):
    """Save the fetched data and metadata with descriptive filenames."""
    freq = meta.get("frequency_short", meta.get("frequency", "unknown")).replace(" ", "")
    title_clean = meta.get("title", "series").replace("/", "-").replace(" ", "_")[:60]

    start_str = start_date if start_date else "FULL"
    end_str = end_date if end_date else "LATEST"

    # Data CSV file
    data_filename = f"{series_id}_{freq}_{start_str}_{end_str}_{title_clean}.csv"
    data_path = OUTPUT_DIR / data_filename
    df.to_csv(data_path, index=False)
    print(f"💾 Saved {len(df)} rows to {data_path}")

    # Metadata JSON file
    meta_filename = f"{series_id}_{freq}_{start_str}_{end_str}_{title_clean}_metadata.json"
    meta_path = OUTPUT_DIR / meta_filename
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"🗂️  Saved metadata to {meta_path}")

    return data_path, meta_path


if __name__ == "__main__":
    print("📊 FRED Series Downloader\n" + "-" * 40)

    # --- Step 1: Metadata
    meta = get_series_metadata(SERIES_ID)
    if not meta:
        exit(1)

    # --- Step 2: Observations (handles None automatically)
    df = fetch_series_data(SERIES_ID, START, END)
    if df.empty:
        print("⚠️  No data downloaded.")
        exit(0)

    # --- Step 3: Save data + metadata
    save_series(df, meta, SERIES_ID, START, END)

    print("✅ All done! Enjoy your data 🚀")
