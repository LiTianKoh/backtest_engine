Session 5 - Performance Analysis
===================================
On top of using returns to quantify strategies, we can use more metrics to measure the robustness of a strategy
1. Sharpe Ratio     → return per unit of risk (volatility)
    Sharpe = (Strategy Return - Risk Free Rate) / Strategy Volatility

    Rough benchmarks:
    < 0.5   → poor
    0.5–1.0 → acceptable
    1.0–1.5 → good
    > 1.5   → excellent (be suspicious of lookahead bias above 2.5)

2. Max Drawdown     → worst peak-to-trough loss ever
    Drawdown on any day = (current equity - peak equity so far) / peak equity

    Peak:    $150,000
    Current: $120,000
    Drawdown: (120,000 - 150,000) / 150,000 = -20%

    Max Drawdown = the single worst drawdown across the entire backtest

3. Calmar Ratio     → annual return ÷ max drawdown
    Calmar = Annualised Return / |Max Drawdown|

    Strategy A: 15% annual return, -30% max drawdown → Calmar = 0.5
    Strategy B: 12% annual return, -10% max drawdown → Calmar = 1.2

    B is the better strategy despite lower returns — you're risking far less to get there

4. Win Rate         → % of trading days with positive return

Looking at the win rate column — all strategies hover around 53–55%. What does that tell you about how these strategies actually make money? Is it by being right more often, or something else?

    Win rate doesn't necessarily equate to making more money. I'm guessing that it's about how much you win when you're right and how much you lose when you're wrong. A loss can easily wipe out 10 wins if the position is not managed properly

    Claude:
    What you described is called profit factor — the ratio of gross wins to gross losses:
    ---------------------------
    Strategy makes 10 trades:
    7 wins  × avg $300 profit  =  $2,100 gross profit
    3 losses × avg $600 loss   = -$1,800 gross loss

    Profit Factor = 2,100 / 1,800 = 1.17   ← barely profitable

    Win Rate = 7/10 = 70%   ← looks great but almost breaks even
    ---------------------------
    A strategy with 40% win rate but 3:1 reward-to-risk ratio crushes a 70% win rate strategy with 1:2 reward-to-risk. Win rate alone is meaningless without knowing the average size of wins vs losses. This is why professional quants almost never talk about win rate in isolation.

The RSI strategy has a Sharpe of 1.22 but only 9.1% annual return. Buy & Hold has 0.73 Sharpe but 13.6% annual return. If you were running a fund and had to pick one, which would you pick and why?

    In the context of my output, I'd pick the buy and hold since it has a higher sharpe ratio and calmar ratio. I understand that the drawdown of the buy and hold is greater but I would probably say that the extra ~5% can be looked over? Correct me if I'm wrong

    Claude:
    More importantly, a -33.3% drawdown is psychologically brutal. Research consistently shows that most investors panic-sell somewhere around -20% to -25%. If you capitulate at -25% and miss the recovery, your actual realised return is far worse than the backtest shows. The drawdown number matters enormously in practice.

    Why your RSI numbers differ from my expected output — you’re running with the institutional cost settings (commission=0.001, slippage=0.002) from Q3. At those cost levels, RSI’s edge is largely destroyed. At retail costs the RSI Sharpe was ~1.22. The strategy is cost-sensitive, which is itself useful information.

===================================