"""
get_stock_info.py
-----------------
Fetches historical company fundamentals from Yahoo Finance (via yfinance)
and saves them as structured CSVs.

✅ Saves automatically:
   • Annual & quarterly financial statements
   • Balance sheets
   • Cash flows
   • Earnings (annual & quarterly)
"""

import yfinance as yf
from pathlib import Path

# =============== USER SETTINGS ===============
TICKER = "AAPL"                     # Example: "AAPL", "TSLA", "NVDA"
OUTPUT_DIR = "data/yFinance/fundamentals"
# ============================================


def save_csv(df, name, ticker, output_dir):
    """Save a DataFrame to CSV if data exists."""
    if df is None or df.empty:
        print(f"ℹ️ No {name} data available for {ticker}.")
        return
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    csv_path = path / f"{ticker}_{name}.csv"
    df.reset_index().to_csv(csv_path, index=False)
    print(f"✅ Saved {name} → {csv_path} ({df.shape[0]} rows)")


def get_fundamentals(ticker, output_dir):
    """Fetch and save main company fundamentals."""
    print(f"\n📊 Fetching fundamentals for {ticker}...")
    t = yf.Ticker(ticker)

    datasets = {
        "financials_annual": t.financials,
        "financials_quarterly": t.quarterly_financials,
        "balance_annual": t.balance_sheet,
        "balance_quarterly": t.quarterly_balance_sheet,
        "cashflow_annual": t.cashflow,
        "cashflow_quarterly": t.quarterly_cashflow,
        "earnings_annual": t.earnings,
        "earnings_quarterly": t.quarterly_earnings,
    }

    for name, df in datasets.items():
        save_csv(df, name, ticker, output_dir)

    print("✅ Done.\n")


if __name__ == "__main__":
    get_fundamentals(TICKER, OUTPUT_DIR)
