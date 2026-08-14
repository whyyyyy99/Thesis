total_return = self.results["cumulative_returns"].tail(1)[0] - 1

returns_mean = self.results["strategy_returns"].mean()
returns_std = self.results["strategy_returns"].std()
if returns_std != 0 and not pl.Series([returns_std]).is_nan()[0]:
    sharpe_ratio = (252**0.5) * returns_mean / returns_std
else:
    sharpe_ratio = float("nan")

drawdowns = (
    self.results["equity_curve"] / self.results["equity_curve"].cum_max() - 1
)
max_drawdown = drawdowns.min()
