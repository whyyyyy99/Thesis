import polars as pl

portfolio = pl.DataFrame({"positions": signals["positions"]})

# Pairs trading
if "Close_1" in self.data.columns and "Close_2" in self.data.columns:
    portfolio = portfolio.with_columns(
        (
            self.data["Close_1"].pct_change() - self.data["Close_2"].pct_change()
        ).alias("asset_returns")
    )
# Single asset trading
elif "Close" in self.data.columns:
    portfolio = portfolio.with_columns(
        self.data["Close"].pct_change().alias("asset_returns")
    )
else:
    raise ValueError("Data does not contain required 'Close' columns")

portfolio = portfolio.with_columns(
    (pl.col("positions").shift(1) * pl.col("asset_returns")).alias("strategy_returns")
)

# Handle potential NaN or inf values
portfolio = portfolio.with_columns(
    pl.when(pl.col("strategy_returns").is_finite())
    .then(pl.col("strategy_returns"))
    .otherwise(0)
    .alias("strategy_returns")
)

portfolio = portfolio.with_columns(
    (1 + pl.col("strategy_returns")).cum_prod().alias("cumulative_returns"),
    (self.initial_capital * pl.col("cumulative_returns")).alias("equity_curve"),
)