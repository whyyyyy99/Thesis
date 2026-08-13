import numpy as np
import polars as pl

total_return = self.results["cumulative_returns"][-1] - 1

returns_mean = self.results["strategy_returns"].mean()
returns_std = self.results["strategy_returns"].std()
if returns_std != 0 and not np.isnan(returns_std):
    sharpe_ratio = np.sqrt(252) * returns_mean / returns_std
else:
    sharpe_ratio = np.nan

drawdowns = (
    self.results["equity_curve"] / self.results["equity_curve"].cum_max() - 1
)
max_drawdown = drawdowns.min()
