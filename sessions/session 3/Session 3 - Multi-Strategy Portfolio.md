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



Notes:
- The weightage of the different strategies is done on a map
- The map contains the strategy names as keys and their corresponding weights as values
- You create a df strategy_returns = pd.DataFrame(index = df.index) to store the different returns from the strategies
- Once computed, create df["portfolio_return"] = strategy_returns.sum(axis = 1) to sum the weighted returns of the multi-strategy portfolio
- New paramter for .plot, linestyle = "--"
===================================