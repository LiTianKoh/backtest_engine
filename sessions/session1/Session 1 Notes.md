Session 1 - First Working Backtest (50-sma vs 200-sma)
===================================
You learn how back testing works

1. Use .rolling(x) to look at datas over the past x days
2. What happens when you change the strategy from 50-sma to 200-sma?
    SMA-200 fires fewer signals overall. The enemy of a trend-following strategy is whipsaw (Choppy market) + spreads + transaction costs

    SMA-50 during a choppy month:
    Price: 450 → 448 → 451 → 449 → 452 → 448
    Signal: OUT → IN → OUT → IN → OUT → IN   ← 5 trades, going nowhere

    SMA-200 during the same month:
    Signal: IN → IN → IN → IN → IN → IN      ← 0 trades, just holds

    However, the trade off of having the SMA-200 would be the reaction speed. In a crash, the SMA-50 would get you out faster compared to the SMA-200.

    So this is the trade off between the two strategies

3. What happens to the equity curve when you introduce the lookahead bias
    The lookahead bias can significantly impact the equity curve by providing an unrealistic view of the strategy's performance. When the strategy uses future information (i.e., the next day's price) to make trading decisions, it can lead to inflated returns during backtesting.

    In the case of the SMA crossover strategy, if we were to use the raw signals without shifting them, the strategy would appear to perform exceptionally well, as it would always "know" the future price movements. This would result in a much steeper equity curve, suggesting that the strategy is highly profitable.

    However, this is not reflective of real-world trading conditions, where traders do not have access to future price data. Once the lookahead bias is removed (by shifting the signals), the equity curve would likely flatten out, showing more realistic returns that account for the actual decision-making process based on historical data.

    The equity curve looks incredible because you never take a loss you didn't know was coming
===================================