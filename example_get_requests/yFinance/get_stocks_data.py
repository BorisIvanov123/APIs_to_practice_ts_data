"""
get_stock_data.py
-----------------
Fetch stock data from Yahoo Finance (via yfinance)
and save it to a CSV file with a dynamic filename.

Smart input handling:
  Fetches full available history using period='max'
  Handles missing start or end dates gracefully
  Auto-fixes too-long intraday/hourly ranges
  Validates inputs and prints summary
"""

import time
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta

# ===========================
# USER SETTINGS — EDIT THESE
# ===========================
TICKER = "SPY"               # Example: "AAPL", "TSLA", "^GSPC"
START_DATE = None             # None → full history -> specify "YYYY-MM-DD" for custom start. Just follow the format
END_DATE = None               # None → latest -> specify "YYYY-MM-DD" for custom end
INTERVAL = "1m"               # "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "1wk", "1mo"
OUTPUT_DIR = "data/yFinance"
# ============================

def validate_inputs(ticker, start, end, interval):
    """Validate and adjust user inputs to prevent common errors."""
    if not ticker or not isinstance(ticker, str):
        raise ValueError("❌ Invalid ticker symbol. Please set a valid string (e.g. 'AAPL').")

    start_dt = datetime.strptime(start, "%Y-%m-%d") if start else None
    end_dt = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()

    if start_dt and end_dt < start_dt:
        raise ValueError(f"❌ END_DATE {end_dt.date()} cannot be before START_DATE {start_dt.date()}.")

    intraday_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]

    # Limit range for intraday intervals if start provided
    if interval in intraday_intervals and start_dt:
        if (datetime.now() - start_dt).days > 730:
            print("⚠️ Range too long for intraday/hourly data — trimming to last 730 days.")
            start_dt = datetime.now() - timedelta(days=730)
        if end_dt > datetime.now():
            end_dt = datetime.now()

    # Case 1: both dates are None → full history (use period='max')
    if start is None and end is None:
        print("ℹ️ Fetching full available history (period='max').")
        return ticker, None, None, interval, "max"

    # Case 2: only start or only end missing → use what is provided
    if start is None:
        print("ℹ️ No START_DATE specified — using earliest available data.")
        start_dt = None
    if end is None:
        end_dt = datetime.now()

    start_str = start_dt.strftime("%Y-%m-%d") if start_dt else None
    end_str = end_dt.strftime("%Y-%m-%d") if end_dt else None
    return ticker, start_str, end_str, interval, None  # period=None means normal date-based fetch


def get_stock_data(ticker, start=None, end=None, interval="1d", output_dir="data", retries=3):
    """Download stock data with retries, summary, and period fallback."""
    ticker, start, end, interval, period = validate_inputs(ticker, start, end, interval)
    filename = f"{ticker}_{interval}_data.csv"

    for attempt in range(1, retries + 1):
        try:
            print(f"📊 Fetching {interval} data for {ticker} (attempt {attempt}/{retries})...")

            if period == "max":
                data = yf.download(ticker, period="max", interval=interval, progress=False, auto_adjust=False)
            else:
                data = yf.download(ticker, start=start, end=end, interval=interval, progress=False, auto_adjust=False)

            if data.empty:
                raise ValueError("No data returned. Possible invalid ticker or unavailable data.")

            # Ensure output folder exists
            path = Path(output_dir)
            path.mkdir(parents=True, exist_ok=True)

            csv_path = path / filename
            data.to_csv(csv_path)
            print(f"✅ Saved to: {csv_path}")

            # Summary
            print("\n📋 SUMMARY")
            print("────────────────────────────")
            print(f"🏷️  Ticker:     {ticker}")
            print(f"⏱️  Interval:   {interval}")
            print(f"🗓️  Start:      {data.index.min().date() if not data.empty else 'N/A'}")
            print(f"🗓️  End:        {data.index.max().date() if not data.empty else 'N/A'}")
            print(f"📊  Rows:       {len(data):,}")
            print(f"📂  Saved File: {csv_path.resolve()}")
            print("────────────────────────────\n")

            return data

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(2)

    print("❌ Failed after multiple attempts. Please check your internet or ticker.")
    return None


if __name__ == "__main__":
    df = get_stock_data(TICKER, START_DATE, END_DATE, INTERVAL, OUTPUT_DIR)
    if df is not None:
        print(df.tail())
