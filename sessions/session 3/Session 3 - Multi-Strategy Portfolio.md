Session 3 - Multi-Strategy Portfolio
===================================
Back in sesion 2, 
# Instead of:
strategy_return = signal × market_return   # all capital in one strategy

# We do:
portfolio_return = (w1 × signal1 + w2 × signal2 + w3 × signal3) × market_return
#                   ↑ weight        ↑ weight        ↑ weight
#                   must sum to 1.0

→ Each strategy has a specific weight

1. The core-satellite portfolio beats equal weight in this output. Look at the weights — why does giving more weight to MA-200 help here? Does that mean you should always overweight your best strategy?

    No. Not sure why

    Claude:
    ========================================
    Looking at your Image 1, RSI alone (249.5%) actually outperforms MA-200 alone (237.1%) in your data. So the core-satellite (60/30/10) — which heavily weights MA — gives 249.5%, while simply moving more weight to RSI (30/60/10) gives 254.5%.

    This looks like "yes, just overweight your best strategy." But here's the trap:
    ---------------------------------------
    You're choosing weights AFTER seeing which strategy won.
    In real life, you make the allocation BEFORE the results.

    2010: "RSI looks best from 2000–2010 data"  → overweight RSI
    2010–2024: MA-200 might have dominated instead
    ---------------------------------------
    The correct answer is: no, you should not always overweight your historical best. What you're seeing is in-sample fitting — the same sin as overfitting. In Session 6 (walk-forward validation) you'll see how to make allocation decisions using only past data, the way a real fund would.
    ========================================

2. Try a portfolio that is RSI-heavy — give it 60% weight, MA 20%, ROC 20%. What do you expect to happen to total return and how smooth the equity curve is? Run it and check.

    I'd expect the total return to be higher and smoother since the RSI alone has better returns than the other two

    Claude:
    ========================================
    Your prediction was right directionally. Going (30/60/10) improved returns from 249.5% → 254.5%. You got lucky here in that RSI happened to be the best individual strategy in this period — the portfolio moves closer to its best component when you overweight it. The whipsaw cost you predicted is real but was outweighed by RSI's strong performance in this window.
    
    Every single active strategy lost to simply buying SPY and doing nothing. This isn't a backtest failure — it's a real and well-documented phenomenon called the equity risk premium. In a 14-year bull market with a few recoveries, market timing strategies repeatedly pay the cost of getting out and then missing the recovery:
    ---------------------------------------
    2020 COVID crash:
    Buy & Hold: -34% in Feb–Mar, then +100% by end of 2021
    MA strategy: got out near the bottom ✓
                but re-entered AFTER the recovery had already started ✗
                missed a significant chunk of the +100% bounce
    ---------------------------------------
    This is why the comparison table you should care about in Session 4 isn't total return — it's return per unit of risk taken. A strategy that makes 250% but never drops more than 15% in a single year is arguably better than Buy & Hold's 445% with a -34% drawdown. That's what Sharpe ratio and max drawdown measure, and that's Session 4.
    ========================================

Notes:
- The weightage of the different strategies is done on a map
- The map contains the strategy names as keys and their corresponding weights as values
- You create a df strategy_returns = pd.DataFrame(index = df.index) to store the different returns from the strategies
- Once computed, create df["portfolio_return"] = strategy_returns.sum(axis = 1) to sum the weighted returns of the multi-strategy portfolio
- New paramter for .plot, linestyle = "--"
===================================