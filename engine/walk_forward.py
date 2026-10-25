import numpy as np
import pandas as pd
from engine.backtester import run_portfolio_backtest

def walk_forward_backtest(df, strategy_weights, train_years = 3, test_years = 1, commission = 0.0005, slippage = 0.0005):
    """
    Walk-forward validation engine.

    Splits the full data into rolling train/test windows.
    Only the TEST periods contribute to the final equity curve.
    This simulates what you would have actually made in real life.

    df               : full price DataFrame with signal columns already built
    strategy_weights : dict of signal_col → weight (same as run_portfolio_backtest)
    train_years      : length of each training window
    test_years       : length of each test window
    """
    periods_per_year = 252
    train_size = periods_per_year * train_years
    test_size = periods_per_year * test_years

    df = df.dropna().copy()
    total_rows = len(df)

    # Store test period results here
    test_results = []
    train_results = []
    window_num = 0

    print(f"\n=== Walk-Forward Validation ===")
    print(f"Train: {train_years}yr | Test: {test_years}yr | Total data: {total_rows} days\n")

# Roll the window forward by test_size each iteration
    start = 0
    while start + train_size + test_size <= total_rows:
        # Define the train and test slices
        train_end = start + train_size
        test_end = train_end + test_size

        train_df = df.iloc[start:train_end]
        test_df = df.iloc[train_end:test_end]

        train_start_date = train_df.index[0].date()
        train_end_date = train_df.index[-1].date()
        test_start_date = test_df.index[0].date()
        test_end_date = test_df.index[-1].date()

        # Run backtest on TEST & TRAIN periods 
        # Starting capital resets to $100k each window for comparability
        result = run_portfolio_backtest(
            test_df,
            strategy_weights,
            commission=commission,
            slippage=slippage
        )

        train_result = run_portfolio_backtest(
            train_df,
            strategy_weights,
            commission=commission,
            slippage=slippage
        )

        # Compute test period Sharpe for this window
        test_returns = result["portfolio_return"].dropna()
        sharpe = (test_returns.mean() / test_returns.std()) * np.sqrt(periods_per_year) if test_returns.std() > 0 else 0

        # Compute train period Sharpe
        train_returns = train_result["portfolio_return"].dropna()
        train_sharpe = (train_returns.mean() / train_returns.std()) * np.sqrt(periods_per_year) if train_returns.std() > 0 else 0

        window_num += 1
        print(f"Window {window_num:>2}  "
              f"\nTrain: {train_start_date} - {train_end_date} | "
              f"Train sharpe: {train_sharpe:.2f}"
              f"\nTest: {test_start_date} - {test_end_date} | "
              f"Test sharpe: {sharpe:.2f}")
        
        test_results.append(result[["portfolio_return"]])
        train_results.append(train_result[["portfolio_return"]])

        # Slide forward by one test period
        start += test_size

    # Stitch all test returns into one continuous series
    all_test_returns = pd.concat(test_results)

    # Build equity curve from stitched returns
    initial_capital = 100_000
    equity_wf = initial_capital * (1 + all_test_returns).cumprod()

    print(f"\nTotal Out-Of-Sample Days: {len(all_test_returns)}")
    print(f"Windows completed: {window_num}")

    return equity_wf, all_test_returns
