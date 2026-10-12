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



===================================