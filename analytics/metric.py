import numpy as np
import pandas as pd

def calculate_metrics(equity_series, signal_series=None, risk_free_rate=0.05, periods_per_year=252):
    """
    Calculate all key performance metrics for a strategy's equity curve.

    equity_series   : pd.Series of portfolio value over time
    risk_free_rate  : annual risk-free rate (default 5% for current US T-bills)
    periods_per_year: 252 for daily data
    """
    equity = equity_series.dropna()

    # ── Daily returns from equity curve ──────────────────────────
    daily_returns = equity.pct_change().dropna()

    # ── 1. Total Return ──────────────────────────────────────────
    total_return = (equity.iloc[-1] / equity.iloc[0]) - 1

    # ── 2. Annualised Return ─────────────────────────────────────
    # How many years did this backtest run?
    n_years = len(daily_returns) / periods_per_year
    # Compound annual growth rate (CAGR)
    annual_return = (1 + total_return) ** (1 / n_years) - 1

    # ── 3. Annualised Volatility ─────────────────────────────────
    # Daily volatility scaled to annual using sqrt(252)
    # Why sqrt? Variance scales linearly with time,
    # so std deviation (sqrt of variance) scales with sqrt(time)
    annual_vol = daily_returns.std() * np.sqrt(periods_per_year)

    # ── 4. Sharpe Ratio ──────────────────────────────────────────
    daily_rf = risk_free_rate / periods_per_year
    excess_returns = daily_returns - daily_rf
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)

    # ── 5. Max Drawdown ──────────────────────────────────────────
    # Rolling maximum equity up to each point in time
    rolling_peak = equity.cummax() # <--- Keep track of the highest point
    # Drawdown at each point = how far below the peak we are
    drawdown = (equity - rolling_peak) / rolling_peak
    max_drawdown = drawdown.min()   # most negative value = worst drawdown

    # ── 6. Calmar Ratio ──────────────────────────────────────────
    # Return per unit of drawdown risk
    calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else np.nan

    # ── 7. Win Rate ──────────────────────────────────────────────
    # % of days the strategy made money
    if signal_series is not None:
        # Only count days we were actually in a position
        active_returns = daily_returns[signal_series.reindex(daily_returns.index).fillna(0) > 0]
        win_rate = (active_returns > 0).sum() / len(active_returns) if len(active_returns) > 0 else 0
    else:
        win_rate = (daily_returns > 0).sum() / len(daily_returns)

    return {
        "Total Return":     f"{total_return * 100:.1f}%",
        "Annual Return":    f"{annual_return * 100:.1f}%",
        "Annual Vol":       f"{annual_vol * 100:.1f}%",
        "Sharpe Ratio":     f"{sharpe:.2f}",
        "Max Drawdown":     f"{max_drawdown * 100:.1f}%",
        "Calmar Ratio":     f"{calmar:.2f}",
        "Win Rate":         f"{win_rate * 100:.1f}%",
    }

def print_metric_table(strategy_dict, signals_dict=None, risk_free_rate=0.0):
    """
    strategy_dict : {"Strategy Name": equity_series, ...}
    signals_dict  : {"Strategy Name": signal_series, ...}  ← optional
    """
    rows = {}
    for name, equity in strategy_dict.items():
        # If a signal was provided for this strategy, pass it through
        signal = signals_dict.get(name) if signals_dict else None
        rows[name] = calculate_metrics(equity, signal_series=signal, risk_free_rate=risk_free_rate)

    # Print table
    metric_name = list(next(iter(rows.values())).keys()) # Turn keys into a list
    col_w = 22

    # Header
    print(f"\n{'Metric':<{col_w}}", end="")
    for names in rows:
        print(f"{names:<{col_w}}", end="")

    print()
    print("-" * (23 + col_w * len(rows)))

    # Rows
    for metric in metric_name:
        print(f"{metric:<{col_w}}", end="")
        for name in rows:
            print(f"{rows[name][metric]:>{col_w}}", end="")
        print()

def plot_drawdown(strategies_dict, title="Drawdown Analysis"):
    """
    Plots the drawdown curve for each strategy over time.
    Drawdown = how far below the previous peak you are at any moment.
    """
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    colors = ["royalblue", "seagreen", "orange", "red", "purple", "gray"]

    for (name, equity), color in zip(strategies_dict.items(), colors):
        eq = equity.dropna()

        # Equity Curve
        ax1.plot(eq.index, eq, label=name, color=color, linewidth=1)

        # Drawdown Curve
        rolling_peak = eq.cummax()
        drawdown = (eq - rolling_peak) / rolling_peak * 100
        ax2.fill_between(drawdown.index, drawdown, 0, color=color, alpha=0.3)
        ax2.plot(drawdown.index, drawdown, label=name, color=color, linewidth=1)

    ax1.set_ylabel("Portfolio Value ($)")
    ax1.set_title(title)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_title("Drawdown (How far below peak at every point)")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    plt.tight_layout()
    # plt.savefig("/Users/litian/Desktop/quant_projects/backtest_engine/sessions/session 5/drawdown_2.png", dpi = 150)
    plt.show()

def plot_wf_comparison(equity_insample, equity_wf, equity_buyhold, title="Walk-Forward vs In-Sample vs Buy & Hold"):
    """
    Plots three equity curves side by side:
    - In-sample (what your backtest claimed)
    - Walk-forward (what you'd have actually made)
    - Buy & Hold (the benchmark)

    The gap between in-sample and walk-forward is your overfitting penalty.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(14, 6))
    plt.plot(equity_insample.dropna(), label="In-Sample (full period)", color="royalblue", linewidth=1, alpha=0.7)    
    plt.plot(equity_wf.dropna(), label="Out-Of-Sample (Walk-Forward)", color="seagreen", linewidth=1, alpha=0.7)    
    plt.plot(equity_buyhold.dropna(), label="Buy & Hold", color="gray", linewidth=1, alpha=0.7)

    plt.title(title)
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True, alpha = 0.3)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    # plt.savefig("/Users/litian/Desktop/quant_projects/backtest_engine/sessions/session 6/wf_results_2", dpi = 150)
    plt.show()

def sharpe(returns, periods_per_year=252):
    r = returns.dropna()

    if len(r) > 1 and r.std() > 0:
        return r.mean() / r.std() * np.sqrt(periods_per_year)
    return np.nan