#!/usr/bin/env python3
"""
Fetch data from any EIA v2 API URL, handling pagination, rate limits,
and optional start/end date filters. Data is saved to a CSV file.

You can paste your full API URL (including query parameters like frequency, data[], facets, etc.)
and the script will handle pagination automatically.

Adds post-processing for the 'period' column to produce a proper timestamp.
"""

import csv
import time
import requests
from urllib.parse import urlencode, urlparse, parse_qs
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime

# === USER CONFIGURATION ======================================================

# Paste your EIA API URL here (from the web-portal)
BASE_URL = "https://api.eia.gov/v2/electricity/operating-generator-capacity/data/?frequency=monthly&data[0]=county&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"

# Optional date range — format YYYY-MM-DD (leave as None for full range)
START_DATE = "2024-12-30"
END_DATE = "2024-12-31"

# Output location
OUTPUT_FILE = Path("data/EIA/eia_data.csv")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Pagination and safety parameters
PAGE_SIZE = 5000  # EIA maximum rows per request
REQUEST_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 5  # retry attempts for transient HTTP errors

# === API KEY LOADING =========================================================
# Always store your API key in a .env file for security and never publish it to Github.
load_dotenv()  # reads .env file
API_KEY = os.getenv("API_KEY_EIA")
if not API_KEY:
    raise ValueError("API_KEY not found. Please set it in your .env file.")

# === FUNCTIONS ==============================================================


def parse_base_url(url: str) -> (str, dict):
    """Split user URL into base endpoint and query parameters dict."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    params = parse_qs(parsed.query)
    return base, params


def fetch_page(base: str, params: dict, offset: int) -> dict:
    """Fetch one page of data from EIA API."""
    params = params.copy()
    params["offset"] = [str(offset)]
    params["length"] = [str(PAGE_SIZE)]
    params["api_key"] = [API_KEY]

    # Apply date filters if specified
    if START_DATE:
        params["start"] = [START_DATE]
    if END_DATE:
        params["end"] = [END_DATE]

    url = f"{base}?{urlencode(params, doseq=True)}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[WARN] Attempt {attempt} failed for offset {offset}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
            else:
                raise
    return {}


def process_period(raw_period: str) -> str:
    """Convert '2024-12-31T00' → '2024-12-31 00:00:00' (ISO format)."""
    try:
        dt = datetime.strptime(raw_period, "%Y-%m-%dT%H")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return raw_period


def write_csv_header(writer, first_page: dict):
    """Write CSV header using keys from the first record."""
    headers = list(first_page["response"]["data"][0].keys())
    if "timestamp" not in headers:
        headers.insert(headers.index("period") + 1, "timestamp")
    writer.writerow(headers)
    return headers


def main():
    base, params = parse_base_url(BASE_URL)
    print(f"[INFO] Fetching from endpoint: {base}")
    print(f"[INFO] API key loaded ✅")

    if START_DATE or END_DATE:
        print(f"[INFO] Date range: {START_DATE or 'beginning'} → {END_DATE or 'latest'}")

    offset = 0
    rows_written = 0
    headers = None

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        while True:
            print(f"[INFO] Fetching rows {offset}–{offset + PAGE_SIZE} ...")
            data_page = fetch_page(base, params, offset)

            if "response" not in data_page or "data" not in data_page["response"]:
                print("[WARN] No valid data in response; stopping.")
                break

            records = data_page["response"]["data"]
            if not records:
                print("[INFO] No more records.")
                break

            # Write header once
            if headers is None:
                headers = write_csv_header(writer, data_page)

            # Write rows with processed timestamp
            for record in records:
                row = []
                for h in headers:
                    if h == "timestamp":
                        row.append(process_period(record.get("period", "")))
                    else:
                        row.append(record.get(h, ""))
                writer.writerow(row)

            rows_written += len(records)
            total = int(data_page["response"].get("total", rows_written))
            print(f"[INFO] Written {rows_written}/{total} rows.")

            if rows_written >= total:
                print("[INFO] All data retrieved.")
                break

            offset += PAGE_SIZE
            time.sleep(REQUEST_DELAY)

    print(f"[SUCCESS] Done. Data saved to: {OUTPUT_FILE.resolve()}")


# === ENTRY POINT =============================================================

if __name__ == "__main__":
    main()
