import numpy as np
import pandas as pd
from analytics.metric import sharpe

def run_universe_backtest(prices, signal_fn, commission=0.0005, slippage=0.0005):
    """
    prices    : DataFrame, rows = dates, columns = tickers
    signal_fn : function(df) -> 0/1 Series, where df has a 'Close' column.
                Must already be shifted (no lookahead), like sma_crossover.
    Returns   : (net_returns DataFrame, trades Series)
    """
    net, trades = {}, {}

    for t in prices.columns:
        px = prices[t].dropna() # For each ticker, the row with no price data will get removed
        """
        Before this line runs, px is a Series:
        Date
        2023-01-02    150.10
        2023-01-03    152.30
        Name: AAPL, dtype: float64

        After df = pd.DataFrame({"Close": px}) runs, it becomes a structured DataFrame:

        Date	Close
        2023-01-02	150.10
        2023-01-03	152.30
        """
        df = pd.DataFrame({"Close" : px})
        sig = signal_fn(df) # The signal function that outputs a df

        flips = sig.diff().abs().fillna(0)
        net[t] = sig * px.pct_change() - flips * (commission + slippage) # Sum the net return including costs like commission and slippage at every entry/exit
        trades[t] = int((flips == 1).sum()) # Find the total number of trades taken

    return pd.DataFrame(net), pd.Series(trades) # Series is 1-dimensional, DF is 2-dimensional
    
def universe_report(prices, net, trades):
    bh = prices.pct_change()

    """
    apply(): To pass every column (or row) of a DF through a function all at once. Instead of using
    for loops to calculate the metric for every stock one by one, .apply() automates the process across
    the dataset
    """
    table = pd.DataFrame({
        "Strat Sharpe": net.apply(sharpe),
        "B&H Sharpe": bh.apply(sharpe),
        "Trades": trades,
    })
    """
    You ideally want to find a strategy that's better than the common Buy & Hold Strategy,
    hence we decide to use a conditional statement to only create tables where the strategy
    performs better than the Buy & Hold in the same universe.
    """
    table["Beats B&H"] = table["Strat Sharpe"] > table["B&H Sharpe"]

    print(table.round(2).to_string()) # Rounding all calculated numbers to 2 dp
    print(f"\nMedian Strategy Sharpe: {table['Strat Sharpe'].median():.2f}")
    print(f"Median Buy & Hold Sharpe: {table['B&H Sharpe'].median():.2f}")
    print(f"Tickers beating B&H: {table['Beats B&H'].sum()} / {len(table)}")

    return table
