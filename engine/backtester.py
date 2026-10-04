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
    """
    # Save the compounded value for the next day's return. 
    # Otherwise, it'll keep resetting to the initial capital
    """
    df["equity_strategy"] = initial_capital * (1 + df["strategy_return"]).cumprod()
    df["equity_buyhold"] = initial_capital * (1 + df["market_return"]).cumprod()

    return df

# Session 3
def run_portfolio_backtest(df, strategy_weights, initial_capital = 100_000):
    """
    Run a backtest for a portfolio of strategies

    Multi-strategy backtest

    strategy_weights: dict mapping signal column name → capital weight
    e.g. {"signal_ma": 0.5, "signal_rsi": 0.3, "signal_roc": 0.2} → A dictionary with key-value pairs
    
    Weights must sum to 1.0.

    On each day, each strategy controls its slice of capital.
    Portfolio return = weighted average of all strategy returns.
    """
    df = df.copy()
    df["market_return"] = df["Close"].pct_change()

    # Validate weights sum to 1
    total_weights = sum(strategy_weights.values())
    if not np.isclose(total_weights, 1.0):
        raise ValueError(f"Weight sum must sum up to 1.0, current {total_weights: .3f}")
    
    # Build a DF of individual strategy returns
    """
    Creates a completely blank DataFrame table with no data columns,
    and assigns it a pre-existing row timeline (index)
    """
    strategy_returns = pd.DataFrame(index = df.index)

    for sig_col, weight in strategy_weights.items():
        strategy_returns[sig_col] = df[sig_col] * df["market_return"] * weight # But how do you know how much to allocate per signal? Or do you just do a trial and error?

    # Portfolio return = sum of all weighted strategy returns
    df["portfolio_return"] = strategy_returns.sum(axis = 1)

    # Calculate portfolio equity curve
    df["equity_portfolio"] = initial_capital * (1 + df["portfolio_return"]).cumprod()
    df["equity_buyhold"] = initial_capital * (1 + df["market_return"]).cumprod()

    # Also store the individual strategy equities for comparison
    for sig_col, weight in strategy_weights.items(): # Have to unpack 'weight' because strategy_weights is a key:value dict, even if you're not using it in the loop
        col = f"equity_{sig_col}"
        df[col] = initial_capital * (1 + df[sig_col] * df["market_return"]).cumprod() # sig_col is either 1 or 0

    return df
