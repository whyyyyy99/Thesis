import numpy as np
import polars as pl

total_return = self.results.get_column("cumulative_returns")[-1] - 1

returns_mean = self.results.get_column("strategy_returns").mean()
returns_std = self.results.get_column("strategy_returns").std()
if returns_std is not None and returns_std != 0 and not np.isnan(returns_std):
    sharpe_ratio = np.sqrt(252) * returns_mean / returns_std
else:
    sharpe_ratio = np.nan

drawdowns = (
    self.results.get_column("equity_curve") / self.results.get_column("equity_curve").cum_max() - 1
)
max_drawdown = drawdowns.min()