Session 4 - Realistic Execution
===================================
Current backtest lacks:
1. Commission - Amount the broker charges per trade. Retail traders pay near $0 commissions but for large funds, large sizes matter
2. Slippages - Delay in order Execution
3. Market impact - For large orders, buying pressure moves prices up before your order is fully filled

Example:
--------------------------------------------------
Signal says: buy SPY at $475.00
Real fill:   $475.00
           + $0.24  slippage (0.05% of price)
           + $0.05  commission
           ────────
Actual cost: $475.29   ← you're already down before you've made anything
--------------------------------------------------

1. The cost model currently charges a flat percentage. What real-world scenario would make slippage worse than 0.05%? Think about what happens when you try to trade a large size in a thinly traded stock.

    I'm guessing when the market is super volatile, so there's a tendency that the market will miss your intended entry by alot of points/dollars. However, in the event that I take large trades in a thinkly traded stock, the lack of resting orders in the order book would mean that my market orders will probably fill the asks above the best ask

    Claude:
    ========================================
    Volatile markets — when news hits, the price gaps instantly. By the time your order reaches the exchange, the price has already moved significantly from where you decided to trade. This is called adverse selection — the market moved because informed participants already acted.

    Thin order book — exactly right. The order book at any moment looks like this:
    ----------------------------
    ASKS (sellers)
    $50.08  ← 200 shares
    $50.06  ← 150 shares
    $50.04  ← 100 shares   ← best ask
    ────────────────────── spread
    $50.02  ← 300 shares   ← best bid
    $50.00  ← 100 shares
    $49.97  ← 80 shares
    BIDS (buyers)
    ----------------------------
    If you want to buy 1,000 shares with a market order, you consume every ask level until you’re filled. Your average fill price ends up at ~$50.07 even though best ask was $50.04. That’s slippage. In a thin book, those ask levels have fewer shares so you climb further up the ladder.
    ========================================

2. Try setting commission=0.001, slippage=0.002 (more realistic for an institutional fund trading large blocks). How much does ROC-20’s return change vs MA-200’s? What does that tell you about which strategies scale better?

    The second image are the returns when commissions and slippages are higher. The strategy that scales better is the one that takes fewer trades

    Claude:
    ========================================
    ----------------------------
    Image 1 (retail costs: 0.05% + 0.05%):
    MA-200  73 trades  →  cost drag  7.3%  →  213.3% return
    ROC    317 trades  →  cost drag 31.7%  →  117.4% return

    Image 2 (institutional costs: 0.10% + 0.20%):
    MA-200  73 trades  →  cost drag  21.9%  →  170.7% return  (dropped 42pp)
    ROC    317 trades  →  cost drag  95.1%  →   15.2% return  (dropped 102pp)
    ----------------------------
    ROC essentially breaks at institutional cost levels — 95% of its gross return is consumed by friction. MA-200 takes a hit but survives. This is why large funds gravitate toward low-turnover, high-conviction strategies — they’re the only ones that remain profitable at scale.
    ========================================

    Right now you’re judging strategies purely by total return. That’s incomplete. A strategy that made 200% but dropped 60% at its worst is not the same as one that made 200% and never dropped more than 10%. Session 5 gives you the tools to tell them apart.
===================================