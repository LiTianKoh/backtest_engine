import os
from datetime import datetime
import numpy as np
import pandas as pd

# ── helpers ───────────────────────────────────────────────────────
"""
• Purpose: Extracts a clean, single-stock DataFrame for ticker t from master tables containing dozens of stocks.
• prices[t].dropna(): Grabs the closing prices for ticker t and strips out missing days (NaN, e.g., before the stock IPO'd).
• .reindex(cols["Close"].index): Forces the volume column to match the exact same valid dates as the closing prices.
"""
def _frame(prices, volumes, t):
    cols = {"Close": prices[t].dropna()}
    if volumes is not None:
        cols["Volume"] = volumes[t].reindex(cols["Close"].index)
    return pd.DataFrame(cols)

"""
• Purpose: Calculates the daily net return of an equal-weighted portfolio across all stocks. P is a 2D NumPy matrix of positions (1 or 0), and R is a matrix of daily percentage returns.
• np.diff(P, axis=0, prepend=P[:1]): Subtracts yesterday's position from today's position (axis=0 moves down rows/time). prepend=P[:1] pads the first day so the array size stays identical and Day 1 doesn't trigger a fake trade.
• np.abs(...): Turns -1 (selling) and +1 (buying) both into 1, counting every trade execution ("flip") where you pay transaction fees (cost).
• (P * R - flips * cost).mean(axis=1): Multiplies positions by returns, subtracts transaction costs, and averages across all columns (axis=1 moves across tickers) for each day.
"""
def _port(P, R, cost): # Portfolio
    """Equal-weight daily net returns. P, R: arrays (days x tickers).
    Unlisted tickers (R filled with 0) behave like cash."""
    flips = np.abs(np.diff(P, axis = 0, prepend = P[:1]))
    return (P * R - flips * cost).mean(axis = 1)

def _sharpe(x):
    return x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else np.nan

def _maxdd(x):
    eq = np.cumprod(1 + x)
    return (eq / np.maximum.accumulate(eq) - 1).min()

# ── lookahead guard ───────────────────────────────────────────────
"""
• Purpose: Catches coding bugs where a signal accidentally peeks into the future (e.g., using .shift(-1) or centering a moving average).
• rng = np.random.default_rng(seed): Initializes a modern NumPy random number generator with a fixed seed so tests are reproducible.
• cut = bool(h.signal(df.iloc[:k + 1]).fillna(False).iloc[-1]): Slices the data at random day k (deleting all future data) and checks what the signal says on that final day (iloc[-1]).
• full = bool(h.signal(df).fillna(False).iloc[k]): Runs the signal on the entire dataset (including the future) and checks what it said on day k.
• bad += cut != full: If the signal changes its mind when future data is hidden, bad increments. If bad > 0, it crashes the program with raise ValueError(...) to stop invalid research immediately.
"""
def check_lookahead(h, prices, volumes = None, n_checks = 25, seed = 0):
    """
    A causal signal gives the same answer on day k whether or not the
    future exists. Cut the data at day k and compare with the full-data value.
    """
    rng = np.random.default_rng(seed) # seed is the starting number used to initialise a random number generator, the same seed value will give the same random results each time.
    bad = 0 # A simple counter to track lookahead violations
    for i in range(n_checks):
        t = rng.choice(prices.columns) # Randomly select a ticker from the available columns in the prices DataFrame
        df = _frame(prices, volumes, t)
        if len(df) < 400: # Ensures that the stock has enough data points for reliable signal testing
            continue

        full = h.signal(df).fillna(False).astype(bool) # Run on full data
        fired = np.flatnonzero(full.to_numpy()[300:-1]) + 300
        if i % 2 == 0 and len(fired) > 0:
            k = int(rng.choice(fired)) # Randomly select a day from the days where the signal fired, ensuring that we test on days when the signal is active
        else:
            k = int(rng.integers(300, len(df) - 1)) # k is a random day within the available data to act as "today"
        cut = bool(h.signal(df.iloc[:k + 1]).fillna(False).iloc[-1]) # Exclude future data
        bad += cut != bool(full.iloc[k]) # To ensure that a real strategy cannot "see" the future, both sides must agree. Prioritizing the past over the future.
    if bad:
        raise ValueError(f"LOOKAHEAD DETECTED in '{h.name}': Signal changed on "
                         f"{bad}/{n_checks} checks when future data was removed.")
    print(f"Lookahead check passed ({n_checks} random cuts)")

# ── the tester ────────────────────────────────────────────────────
# h -> Hypothesis with a specific trading strategy build from the Hypothesis class (blueprint)
def test(h, prices, volumes=None, start=None, end =None, commission=0.0005, slippage=0.0005, n_shuffles=200, seed=0, log=True):
    cost = commission + slippage
    check_lookahead(h, prices, volumes)

    """
    • prices.pct_change(): Converts raw stock prices into daily percentage returns.
    • Warm-up slicing (pos.loc[start:end]): Runs h.positions() across the entire dataset first so long indicators (like a 200-day moving average) have enough historical data to warm up before slicing down to the requested start and end dates.
    • .to_numpy(): Converts pandas DataFrames into raw NumPy arrays (P, R, valid), which execute math 10x to 100x faster.
    • in_mask = (P == 1) & valid: Creates a boolean grid marking exact ticker-days where you were actively holding a position (1) and the stock was actively listed on the exchange (valid).
    """
    # Positions on the FULL history (so indicators are warmed up), then cut to the evaluation window
    rets = prices.pct_change()
    pos = pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)
    for t in prices.columns:
        pos[t] = h.positions(_frame(prices, volumes, t))
    pos, rets = pos.loc[start:end], rets.loc[start:end]

    P = pos.fillna(0).to_numpy()
    R = rets.fillna(0).to_numpy()
    valid = rets.notna().to_numpy()
    in_mask = (P == 1) & valid # Creates a 2D boolean grid marking active positions. P == 1 means we are holding the position, valid means the stock was listed.
    flips = np.abs(np.diff(P, axis=0, prepend=P[:1]))

    if in_mask.sum() == 0:
        print(f"'{h.name}' never entered a position in this window.")
        return None
    
    """
    • with np.errstate(...): Temporarily suppresses warnings if a stock had zero valid days (dividing 0 / 0).
    • Demeaning (R - mean_all): Subtracts each stock's own average daily return from its daily returns (Rd). In a roaring bull market, buying randomly makes money; demeaning proves whether your signal actually beats the stock's baseline drift.
    • t_stat: Calculates the statistical t-score of your edge. A t_stat > 3 indicates the edge is highly unlikely to be random noise.
    • drag & net_edge: Calculates the average fee paid per day held (flips.sum() * cost / in_mask.sum()) and subtracts it from your raw edge.
    • breadth: Checks what percentage of individual stocks actually made a profit (edge_t > 0). This prevents a single lucky outlier stock (like Nvidia or Apple) from masking a strategy that fails on 90% of other stocks.
    """
    # Demean each ticker's returns so "edge" means: better than that ticker's own average day (removes the bull-market drift)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean_all = R.sum(0) / valid.sum(0) # Sums each stock's returns and divides by the number of valid days to give the stock's average daily returns
        Rd = np.where(valid, R - mean_all, 0.0) # Subtract the stock's average daily return from its daily returns

        # EDGE (pooled) + COSTS
        r_in = Rd[in_mask] # Create a 1D list of excess returns on every stock-day you were active
        edge = r_in.mean()
        t_stat = edge / (r_in.std(ddof=1) / np.sqrt(len(r_in)))
        drag = flips.sum() * cost / in_mask.sum() # To find the average daily cost drag
        net_edge = edge - drag # Subtract the drag from the raw edge to show what you actually earned

        # BREADTH: per ticker, not edge > 0?
        n_in_t = in_mask.sum(0) # Calculates the number of days you held a position for each stock
        edge_t = (Rd * in_mask).sum(0) / n_in_t - flips.sum(0) * cost / n_in_t # Same equation as net_edge
        traded = n_in_t > 0 # Filter out the stocks you actually traded at least once
        breadth = (edge_t[traded] > 0).mean() # Checks which traded stocks were profitable

    """
    • Purpose: Tests if your strategy is smarter than random luck.
    • np.roll(P, int(k), axis=0): Takes your entire block of buy/sell positions and shifts them circularly in time by k random days (wrapping the bottom back to the top). This preserves your exact trade frequency and holding durations while severing any connection to real market timing.
    • p_val: Compares your real Sharpe ratio (obs) against 200 randomized versions (null). If fewer than 5% of random shuffles beat your strategy (p_val < 0.05), the timing is statistically significant.
    """
    # LUCK: same strategy, positions circularly shifted in time.
    # Keeps exposure, holding lengths and market-wide clustering;
    # destroys any real link between signal and returns.
    rng = np.random.default_rng(seed)
    n = len(P)
    obs = _sharpe(_port(P, R, cost)) # Compressed Sharpe Ratio into a single daily portfolio value
    ks = rng.integers(n // 10, n - n // 10, size=n_shuffles) # An array of 200 random shift amounts/days used to scramble my strategy's timeline
    null = np.array([_sharpe(_port(np.roll(P, int(k), axis=0), R, cost)) for k in ks]) # The distribution of 200 "random/fake" Sharpe Ratios
    """
    In traditional statistics textbooks, you look up a p-value in a table because you assume your data follows a clean theoretical bell curve (a normal distribution).
    However, financial returns do not follow a clean bell curve—they have fat tails, volatility clustering, and market crashes.

    Why add +1?
    • Prevents an impossible p = 0.000: If your strategy beats all 200 random shuffles (np.sum(...) == 0), dividing 0 / 200 would claim your p-value is 0.0. 
    In statistics, a empirical simulation can never prove a 0% probability of luck—it can only prove the probability is smaller than your sample resolution. 
    With + 1, beating all 200 shuffles gives \(1 / 201 \approx 0.00497\) (meaning \(p < 0.005\)).

    • Treats your real strategy as one valid outcome: Under the null hypothesis (the assumption that your strategy has zero real skill and is just another random timeline), 
    your actual historical result (obs) is simply 1 out of \(N + 1\) equally likely random possibilities (\(200 \text{ shuffles} + 1 \text{ original} = 201 \text{ total}\)). 
    Including your observation in both the numerator and denominator keeps the test mathematically unbiased.
    """
    p_val = (1 + np.sum(null >= obs)) / (n_shuffles + 1) # It’s the probability of a Sharpe at least this high if the timing were random

    # VS BUY & HOLD
    strat = _port(P, R, cost)
    bh = _port(np.ones_like(P), R, 0.0) # Creates a new Numpy array of the exact same shape and size as P, filled entirely with ones

    exposure = in_mask.sum() / valid.sum() # Percentage of the total available market days that your money is actively invested in stocks
    entries = int(((np.diff(P, axis=0, prepend=P[:1])) == 1).sum())
    bp = 1e4 # Converts decimal returns into basis points (0.0001 = 1 bp, a standard Wall Street unit for small percentages).

    """
    • checks: Evaluates your strategy against 5 strict institutional rules (Sample Size, Statistical Significance, Survivability after Costs, Luck p-value, and Broad Applicability across tickers) and prints [PASS] or [FAIL].
    • if log:: Appends a single summary row to "research_log.csv". header=not os.path.exists(...) writes column headers only if the CSV file is being created for the very first time.
    • return {...}: Returns a dictionary containing the daily net return table, position matrix, and key metrics so you can plot equity curves or analyze the results further.
    """
    checks = {
        "SAMPLE   >= 30 entries":        entries >= 30, # Requires at least 30 trades across all stocks to be statistically valid
        "EDGE     t-stat > 3":            t_stat > 3, # Requires a t-statistic greater than 3 for for all trades combined
        "COSTS    net edge > 0":          net_edge > 0, # Requires the net edge to be positive after costs across the pooled portfolio
        "LUCK     p < 0.05":              p_val < 0.05, # Requires a p-value less than 0.05 for equal-weighted portfolio's Sharpe Ratio
        "BREADTH  >= 60% of tickers":     breadth >= 0.60, # Requires at least 60% of tickers to have net_edge to be positive
    }

    first, last = pos.index[0].date(), pos.index[-1].date()
    hold = f"hold {h.holding}d" if h.holding else "hold while true"
    print(f"\n=== {h.name}  ({hold}) ===")
    print(f"Window {first} → {last}   Tickers: {P.shape[1]}   "
          f"Entries: {entries}   Days in market: {exposure*100:.1f}%")
    print(f"\n  Gross edge per day held : {edge*bp:+.1f} bp   (t = {t_stat:.1f})")
    print(f"  Cost drag per day held  : {drag*bp:.1f} bp")
    print(f"  Net edge per day held   : {net_edge*bp:+.1f} bp")
    print(f"  Tickers with net edge > 0: {breadth*100:.0f}%")
    print(f"  Strategy Sharpe         : {obs:.2f}   "
          f"(random-timing median {np.median(null):.2f}, p = {p_val:.3f})")
    print(f"  Buy & Hold Sharpe       : {_sharpe(bh):.2f}")
    print(f"  Max drawdown            : {_maxdd(strat)*100:.1f}%  "
          f"vs B&H {_maxdd(bh)*100:.1f}%")
    print()
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("\n  Passing every check is necessary, not sufficient. "
          "Next stop: the holdout window.")

    if log:
        row = pd.DataFrame([{
            "time": datetime.now().isoformat(timespec="seconds"),
            "name": h.name, "holding": h.holding, "start": first, "end": last,
            "exposure": round(exposure, 4), "edge_bp": round(edge * bp, 2),
            "t_stat": round(t_stat, 2), "net_edge_bp": round(net_edge * bp, 2),
            "sharpe": round(obs, 3), "p_value": round(p_val, 4),
        }])
        row.to_csv("research_log.csv", mode="a", index=False,
                   header=not os.path.exists("research_log.csv"))

    net = pd.DataFrame(P * R - flips * cost, index=pos.index, columns=pos.columns)
    return {"net": net, "pos": pos, "edge_bp": edge * bp, "t": t_stat,
            "p": p_val, "sharpe": obs, "checks": checks}