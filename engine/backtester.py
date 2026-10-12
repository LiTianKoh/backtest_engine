import pandas as pd
import numpy as np

# Session 2
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

# Session 4
def apply_costs(df, signal_col, commission=0.0005, slippage=0.0005):
    """
    Detects trades (signal changes) and applies cost on those days.

    commission : fraction of trade value charged per side
                 0.0005 = 0.05% per trade (both entry and exit)
    slippage   : fraction of price you lose on fill
                 0.0005 = 0.05% adverse fill per side

    Total round-trip cost = 2 × (commission + slippage)
    e.g. default = 2 × 0.10% = 0.20% per round trip
    """
    df = df.copy()

    # Detect signal transitions:
    # diff() gives: +1 where signal went 0→1 (entry)
    #               -1 where signal went 1→0 (exit)
    #                0 where signal didn't change (hold)
    signal_diff = df[signal_col].diff().abs()
    # abs() treats both entries and exits as trade events

    # Cost is applied on any day a trade occurs
    # Both commission and slippage are paid per side
    total_cost_per_trade = signal_diff * (commission + slippage)
    df["cost"] = total_cost_per_trade

    # Print trade summary
    n_trades = int((df[signal_col].diff().abs() == 1).sum())
    total_cost_pct = df["cost"].sum() * 100 # Commmission and slippage are in %, so have to convert back to %
    print(f"[{signal_col}] Trades: {n_trades} | "
          f"Total cost drag: {total_cost_pct:.2f}%")
    
    return df["cost"]

# Session 3
def run_portfolio_backtest(df, strategy_weights, initial_capital = 100_000, commission=0.0005, slippage=0.0005):
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
    costs_cache = {}
    print("\n=== Trade Cost Summary ===")

    for sig_col, weight in strategy_weights.items():
        raw_returns = df[sig_col] * df["market_return"] # But how do you know how much to allocate per signal? Or do you just do a trial and error?
        costs = apply_costs(df, sig_col, commission, slippage) # Apply costs to each strategy's raw return
        costs_cache[sig_col] = costs # Store the costs for later use if needed
        net_returns = raw_returns - costs
        strategy_returns[sig_col] = net_returns * weight

    # Portfolio return = sum of all weighted strategy returns
    df["portfolio_return"] = strategy_returns.sum(axis = 1)

    # Calculate portfolio equity curve
    df["equity_portfolio"] = initial_capital * (1 + df["portfolio_return"]).cumprod()
    df["equity_buyhold"] = initial_capital * (1 + df["market_return"]).cumprod()

    # Also store the individual strategy equities for comparison
    for sig_col in strategy_weights: # Only keys needed
        net_returns = df[sig_col] * df["market_return"] - costs_cache[sig_col]

        col = f"equity_{sig_col}"
        df[col] = initial_capital * (1 + net_returns).cumprod() # sig_col is either 1 or 0

    return df
