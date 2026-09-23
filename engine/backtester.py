import pandas as pd
import numpy as np

def run_backtest(df, signal_col = "signal", initial_capital = 100_000):
    """
    Generic backtest engine. Take any df with column 'signal' and a 'Close' column

    Returns the same df with equity columns added
    """
    df = df.copy() # Avoid modifying the original df, it clones it

    # Daily market returns
    df["market_return"] = df["Close"].pct_change()

    #Strategy return: Only returns when signal is 1
    df["strategy_return"] = df[signal_col] * df["market_return"]

    # Equity Curves
    df["equity_strategy"] = initial_capital * (1 + df["strategy_return"]).cumprod() # Save the compounded value for the next day's return. Otherwise, it'll keep resetting to the initial capital
    df["equity_buyhold"] = initial_capital * (1 + df["market_return"]).cumprod()

    return df
