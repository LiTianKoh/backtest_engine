import yfinance as yf
import pandas as pd

UNIVERSE = {
    "Tech":       ["AAPL", "MSFT", "AMD", "ORCL"],
    "Finance":    ["JPM", "BAC", "GS", "MS", "BLK", "AXP"],
    "Healthcare": ["JNJ", "UNH", "LLY", "ABT", "MRK", "TMO"],
    "Consumer":   ["AMZN", "HD", "MCD", "NKE", "SBUX", "TGT"],
    "Energy":     ["XOM", "CVX", "COP", "SLB", "PSX", "VLO"],
}
TICKERS = [t for group in UNIVERSE.values() for t in group]

def fetch_universe(tickers = TICKERS, start="2010-01-01", end="2024-01-01"):
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"]
    prices = prices.dropna(how = "all") # Removes row(dates) where all tickers have missing data(NaN). If a row has data for at least one ticker, that date is kept

    late = prices.isna().sum()
    print(f"Shape: {prices.shape}")
    print("Tickers with missing history:\n", late[late > 0]) # Displays the tickers with missing data
    return prices