import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from engine.backtester import run_backtest
from strategies.signals import sma_crossover, rsi_mean_reversion, rate_of_change_momentum

# --- Fetch Data ---
raw = yf.download("SPY", start = "2010-01-01", end = "2024-01-01", auto_adjust = True, progress = False)

# Fix for newer yfinance: flatten the MultiIndex columns
# Before: ("Close", "SPY"), ("Volume", "SPY")
# After:  "Close", "Volume"
if isinstance(raw.columns, pd.MultiIndex):
    raw = raw.droplevel(axis=1, level=1) # .droplevel - removes specific index or column levels from a MultiIndex DF or Series

df = raw[["Close", "Volume"]].copy()
# df.columns = ["close", "volume"] # Renaming the columns to lower_case

# Confirm it's clean
print(df.info())
print(df.head(3))

# --- Build Signal ---
df["signal_ma"] = sma_crossover(df, window = 200)
df["signal_rsi"] = rsi_mean_reversion(df, window = 14, oversold = 30, overbought = 70)
df["signal_roc"] = rate_of_change_momentum(df, window = 20)

# --- Run each backtest ---
results = {}

for name, col in [
    ("MA-200", "signal_ma"),
    ("RSI MeanRev (30,70)", "signal_rsi"), 
    ("ROC Momentum", "signal_roc")
]:
    out = run_backtest(df, signal_col=col)

    """
    results = {
    "MA-200":         [100000, 100100, 100200, ...], # MA data safely saved here
    "RSI MeanRev":     [100000, 99800,  100500, ...], # RSI data safely saved here
    "ROC Momentum": [100000, 101200, 100900, ...]  # ROC data safely saved here
    }
    """
    results[name] = out["equity_strategy"]

# --- Build Comparison Table ---
INITIAL = 100_000
print(f"\n{'Strategy':<20} {'Final Equity':<12} {'Total Return %':>13} {'Days In Market':>15}")
print("-" * 65)

for name, equity in results.items():
    clean = equity.dropna() # Remove any na values
    final = clean.iloc[-1] # Get the final equity value for each strategy
    returns = ((final / INITIAL) - 1) * 100 # Get return gains in %

    # count days in market
    sig_col = {
        "MA-200": "signal_ma",
        "RSI MeanRev (30,70)": "signal_rsi",
        "ROC Momentum": "signal_roc"
    }[name] # [name] extracts the value(equity) from the key(name) so that can pass the dict into the df in the next line
    days_in = int(df[sig_col].sum()) # No. of days you're holding
    # entries = (df[sig_col].diff() == 1).sum() # No. of times you entered
    print(f"{name:<20} ${final:>11,.0f} {returns:>12.1f}% {days_in:>15,}")

# Buy & Hold baseline
bh = run_backtest(df, signal_col="signal_ma") # reuse df
bh_final = bh["equity_buyhold"].dropna().iloc[-1]
bh_returns = ((bh_final / INITIAL) - 1) * 100
print(f"{'Buy & Hold':<20} ${bh_final:>11,.0f} {bh_returns:>12.1f}% {'3523':>15}")

# --- Plot ---
plt.figure(figsize=(14, 6))
for name, equity in results.items():
    plt.plot(equity.dropna().index, equity.dropna(), linewidth = 1.5, label = name)
plt.plot(
    bh["equity_buyhold"].dropna().index,
    bh["equity_buyhold"].dropna(),
    color = "gray", linewidth = 1.2, alpha = 0.6, label = "Buy & Hold"
)
plt.title("Strategy Comparison: SPY 2010-2023")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid(True, alpha = 0.3)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
# plt.savefig("/Users/litian/Desktop/quant_projects/backtest_engine/sessions/session 2/session2_comparison_2.png", dpi = 150)
plt.show()