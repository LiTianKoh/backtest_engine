import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ====== 1. Fetch SPY price data ======
"""
auto_adjust = True (Default): Adjusts historical stock prices (Open, Close, High, Low) for stock splits and dividends
auto_adjust = False: Does not adjust historical stock prices, including an extra 'Adj Close' column

progress = Controls whether a visual progress bar is shown in your console or notebook while downloading data for multiple tickers
"""
raw = yf.download("SPY", start = "2010-01-01", end = "2024-01-01", auto_adjust = True, progress = False)

df = raw[["Close", "Volume"]].copy()
df.columns = ["Close", "Volume"]

print("=== Data Overview ===")
print(df.info())
print()
print(df.head())
print()
print(df.tail())

# ====== 2. Building the signal ======
df["sma_50"] = df["Close"].rolling(50).mean() # Create a new column named "sma_50"
print("=== Moving Average (First 55 rows) ===")
"""
0 to 48 won't have data since it doens't cover the 50 day window.
Only from the 49th row onward can the SMA be calculated.
"""
print(df[["Close", "sma_50"]].head(55))

# ===== 3. Generating signals =====
"""
1.0 - Long SPY
0.0 - Be in cash (flat)
np.where(condition, value_if_true, value_if_false)
"""
df["raw_signal"] = np.where(df["Close"] > df["sma_50"], 1.0, 0.0) # <- Lookahead bias!

"""
Even thought the SMA is already calculated, the SPY hasn't closed above it yet.
So you can't be sure if the price is going to close above or below the SMA.
Hence to accurately give a signal, we are only able to take the appropriate trade the next day.
"""
df["signal"] = df["raw_signal"].shift(1) # <- Remove lookahead bias by shifting the signal down by 1 day/row
# df["signal"] = df["raw_signal"] <- Lookahead bias

print("=== Signal Check ===")
print(df[["Close", "sma_50", "raw_signal", "signal"]].iloc[48:56])

# ===== 4. Compute daily returns ======
"""
.pct_change() - Gives the % change from previous day's close to today's close
"""
df["market_return"] = df["Close"].pct_change()

# ===== 5. Strategy Return =====
"""
If 1.0, you held SPY -> Earn market_return
If 0.0, you were is cash -> Earn 0
"""
df["strategy_return"] = df["signal"] * df["market_return"]

print("=== Return Comparison (First 30 active days) ===")
active = df[df["signal"].notna() & (df["signal"] > 0)].head(30) # Filter rows with active signals that are 1.0 and doesn't have NaN
print(active[["Close", "signal", "market_return", "strategy_return"]])

# ===== 6. Equity Curve =====
INITIAL_CAPITAL = 100_000
"""
.cumprod() - Cumulative product of (1 + daily_return) gives the growth multiplier
e.g. if returns were +2%, -1%, +3%:
(1.02) × (0.99) × (1.03) = 1.0393 → 3.93% total return
"""
df["equity_strategy"] = INITIAL_CAPITAL * (1 + df["strategy_return"]).cumprod() # Equity of strategy, only enter when the signal is 1.0
df["equity_buyhold"] = INITIAL_CAPITAL * (1 + df["market_return"]).cumprod() # Equity of just buying and holding SPY at the start with all the capital

df_clean = df.dropna(subset = ["signal"]) # Drop rows with NaN in the "signal" column, since we can't trade on those days

print("=== Final Results ===")
final_strategy = df_clean["equity_strategy"].iloc[-1]
final_buyhold = df_clean["equity_buyhold"].iloc[-1]
print(f"Strategy final value: $ {final_strategy:,.0f}") # : tells python that I want to format the number inside. , adds a commas every 3 digits. 
print(f"Buy and hold final value: $ {final_buyhold:,.0f}")
print(f"Strategy returns: {(final_strategy / INITIAL_CAPITAL - 1) * 100:.1f}%")
print(f"Buy and hold returns: {(final_buyhold / INITIAL_CAPITAL - 1) * 100:.1f}%")

# ===== 7. Visualization =====
"""
.subplots(number_of_rows, number_of_columns, figsize = (width_in_inches, height_in_inches), sharex = True/False)
sharex = True: Share the x-axis between the two subplots -> Only applies if you use multiple subplots
sharey = True: Share the y-axis between the two subplots -> Only applies if you use multiple subplots
"""
fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (14, 8), sharex = True) # ax1 and ax2 are separate plots

"""
Top Panel: Equity Curves
"""
ax1.plot(df_clean.index, df_clean["equity_strategy"],
         label = "SMA Crossover Strategy", color = "royalblue", linewidth = 1.5) # .index() - retrieves the row labels of the DataFrame
ax1.plot(df_clean.index, df_clean["equity_buyhold"],
         label = "Buy & Hold Strategy", color = "gray", linewidth = 1.2, alpha = 0.7) # alpha - Transparency level
ax1.set_ylabel("Portfolio Value ($)")
ax1.set_title("50-SMA Crossover Strategy vs Buy & Hold (2010-2023)")
ax1.legend()
"""
.set_major_formatter() - Formats the numbers on the y-axis as clean currency values (10,000 → $10,000)
.FuncFormatter() - A function that takes two arguments: the tick value and the tick position
lambda x, _: f"${x:,.0f}" - x is the tick value, _ is the tick position (not used), f"${x:,.0f}" - formatting
"""
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax1.grid(True, alpha = 0.3) # Adds background gridlines to the plot

"""
Bottom Panel: SPY Prices with SMA overlay and coloured background
"""
ax2.plot(df_clean.index, df_clean["Close"], label = "SPY Price", color = "black", linewidth = 0.8)
ax2.plot(df_clean.index, df_clean["sma_50"], label = "50-SMA", color = "orange", linewidth = 1.2)

"""
Shade regions where we are long in the market
"""
ax2.fill_between(df_clean.index, df_clean["Close"].min(), df_clean["Close"].max(),
                 where = df_clean["signal"] == 1.0, 
                 alpha = 0.1, color = "green", label = "Long Position")
ax2.set_ylabel("SPY Price ($)")
ax2.legend()
ax2.grid(True, alpha = 0.3) # Adds background gridlines to the plot

plt.tight_layout() # Automatically adjusts the spacing of your chart so nothing overlaps
# plt.savefig("session1_results.png", dpi = 150)
# plt.show()
# print("Chart saved to session1_results.png")
print(df.columns)