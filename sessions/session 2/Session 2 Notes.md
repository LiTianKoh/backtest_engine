Session 2 - Hypothesis Testing
===================================
1. SIGNAL      → a number computed from historical data
                 e.g. "5-day rate of change"

2. THRESHOLD   → the rule that converts signal to action
                 e.g. "if signal > 0, go long"

3. HOLDING     → how long you stay in
                 e.g. "hold for 1 day, re-evaluate daily"

4. EXIT        → what makes you close the position
                 e.g. "signal turns negative"

If you can't fill in the above 4, your hypothesis isn't ready yet

1. Look at the RSI strategy. It's only in the market 17% of the time yet still generated 98% return. Does that make it a bad strategy or an interesting one? Think about what you could do with the other 83% of the time when you're sitting in cash.

    Based on your output alone, because I got a completely different output. I would think it's not a bad strategy, it's probably highly selective hence having a low exposure. So I would think for the remaining 83% would be used on other strategies with higher exposure?

    Claude:
    What you described is called a core-satellite allocation — it's standard practice at hedge funds:
    ========================================
    Total Capital: $100,000
    │
    ├── Core (70%) → $70,000 in a high-exposure strategy
    │   e.g. MA-200 trend follow, ~60% time in market
    │   Captures broad market returns
    │
    └── Satellite (30%) → $30,000 in selective strategies
        e.g. RSI mean reversion, ~17% time in market
        Fires only on high-conviction setups
    ========================================
    The satellite strategies are valuable precisely because they're selective. When RSI drops below 30, something has genuinely sold off hard — that's a higher quality signal than "price is above a moving average." You're not trying to always be in the market. You're trying to be in the right moments.

    The compounding insight: if both strategies are running simultaneously and their signals don't overlap much, you get diversification across time — you're never sitting 100% idle.

    This is exactly what Session 3 will build.

2. Try changing the RSI thresholds from (30, 70) to (40, 60). What do you expect to happen to "Days in Market" and total return before you run it? Then run it and see if your intuition was right.

    I would think the exposure of the RSI strategy would increase, but profitability may not be as high as it's likely to be disrupted by whipsawing.

    Claude:
    You correctly identified whipsaw as the risk. But there's a second effect that actually matters more:
    ========================================
    RSI thresholds (30, 70) — original:
    Entry signal fires when RSI < 30
    Asset has fallen HARD and FAST
    The market is genuinely panicking
    → Large expected bounce, strong signal quality

    RSI thresholds (40, 60) — tightened:
    Entry signal fires when RSI < 40
    Asset has just had a bad few days, not a real selloff
    → Smaller expected bounce, weak signal quality
    ========================================
    The logic of RSI mean reversion depends on extremes. At RSI=28 the market is genuinely oversold. At RSI=39 it's just had a rough week. The signal quality degrades as you move thresholds toward the centre.

    So tightening from (30,70) to (40,60) hits you twice:
    ========================================
    Effect 1 — more trades  → more whipsaw costs        (you got this)
    Effect 2 — weaker entry → smaller bounce per trade  (the deeper reason)
    ========================================
===================================