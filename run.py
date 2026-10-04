import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from engine.backtester import run_backtest, run_portfolio_backtest
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

# --- Portfolio weightage (Session 3) ---
weight = {
    "signal_ma": 1/3,
    "signal_rsi": 1/3,
    "signal_roc": 1/3,
}

# --- RSI-heavy portfolio (To answer Session 2's Q2 intuition) (Session 3) ---
# Core: MA trend follow. Satellite: RSI mean reversion
weight_core_satellite = {
    "signal_ma": 0.6,
    "signal_rsi": 0.3,
    "signal_roc": 0.1,
}

# --- Run both portfolios (Session 3) ---
result_equal = run_portfolio_backtest(df, strategy_weights = weight)
result_cs = run_portfolio_backtest(df, strategy_weights = weight_core_satellite)

# # --- Run each backtest (Session 2) ---
# results = {}

# for name, col in [
#     ("MA-200", "signal_ma"),
#     ("RSI MeanRev (30,70)", "signal_rsi"), 
#     ("ROC Momentum", "signal_roc")
# ]:
#     out = run_backtest(df, signal_col=col)

#     """
#     results = {
#     "MA-200":         [100000, 100100, 100200, ...], # MA data safely saved here
#     "RSI MeanRev":     [100000, 99800,  100500, ...], # RSI data safely saved here
#     "ROC Momentum": [100000, 101200, 100900, ...]  # ROC data safely saved here
#     }
#     """
#     results[name] = out["equity_strategy"]

# --- Build Comparison Table ---
INITIAL = 100_000

def summarise(name, equity_series):
    clean = equity_series.dropna()
    final = clean.iloc[-1]
    returns = ((final / INITIAL) - 1) * 100
    print(f"{name:<30} ${final:>11,.0f} {returns:>12.1f}%")

print(f"\n{'Portfolio':<30} {'Final Equity':<12} {'Total Return %':13}")
print("-" * 58)

summarise("Custom Weight (33/33/33)", result_equal["equity_portfolio"])
summarise("Core-Satellite (60/30/10)", result_cs["equity_portfolio"])
summarise("MA-200", result_equal["equity_signal_ma"])
summarise("RSI", result_equal["equity_signal_rsi"])
summarise("ROC-20", result_equal["equity_signal_roc"])
summarise("Buy & Hold", result_equal["equity_buyhold"])

# --- Session 2 ---
# for name, equity in results.items():
#     clean = equity.dropna() # Remove any na values
#     final = clean.iloc[-1] # Get the final equity value for each strategy
#     returns = ((final / INITIAL) - 1) * 100 # Get return gains in %

#     # count days in market
#     sig_col = {
#         "MA-200": "signal_ma",
#         "RSI MeanRev (30,70)": "signal_rsi",
#         "ROC Momentum": "signal_roc"
#     }[name] # [name] extracts the value(equity) from the key(name) so that can pass the dict into the df in the next line
#     days_in = int(df[sig_col].sum()) # No. of days you're holding
#     # entries = (df[sig_col].diff() == 1).sum() # No. of times you entered
#     print(f"{name:<20} ${final:>11,.0f} {returns:>12.1f}% {days_in:>15,}")

# # Buy & Hold baseline
# bh = run_backtest(df, signal_col="signal_ma") # reuse df
# bh_final = bh["equity_buyhold"].dropna().iloc[-1]
# bh_returns = ((bh_final / INITIAL) - 1) * 100
# print(f"{'Buy & Hold':<20} ${bh_final:>11,.0f} {bh_returns:>12.1f}% {'3523':>15}")

# --- Plot ---
plt.figure(figsize=(14, 6))
# for name, equity in results.items():
#     plt.plot(equity.dropna().index, equity.dropna(), linewidth = 1.5, label = name)
# plt.plot(
#     bh["equity_buyhold"].dropna().index,
#     bh["equity_buyhold"].dropna(),
#     color = "gray", linewidth = 1.2, alpha = 0.6, label = "Buy & Hold"
# )

plt.plot(result_equal["equity_portfolio"].dropna(), linewidth = 1.5, label = "Equal Weight Portfolio (33/33/33)", color = "royalblue")
plt.plot(result_cs["equity_portfolio"].dropna(), linewidth = 1.5, label = "Core-Satellite Portfolio (60/30/10)", color = "seagreen")
plt.plot(result_equal["equity_portfolio"].dropna(), linewidth = 1.5, label = "Buy & Hold", color = "gray", alpha = 0.6)

# Individual strategies in the background
for col, name, color in [
    ("equity_signal_ma", "MA-200", "orange"),
    ("equity_signal_rsi", "RSI", "red"),
    ("equity_signal_roc", "ROC", "purple"),
]:
    plt.plot(result_equal[col].dropna(), linewidth = 0.8, label = name, color = color)

plt.title("Multi-Strategy Portfolio vs Individual Strategies (SPY 2010-2023)")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid(True, alpha = 0.3)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
plt.savefig("/Users/litian/Desktop/quant_projects/backtest_engine/sessions/session 3/session3_multiportfolio_comparison1.png", dpi = 150)
plt.show()