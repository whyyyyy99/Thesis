# Ensure 'Date' column is present in signals DataFrame
if "Date" not in signals.columns:
    raise ValueError("'Date' column is missing from the signals DataFrame")

# Pairs trading
if "Close_1" in self.data.columns and "Close_2" in self.data.columns:
    asset_returns = (
        self.data["Close_1"] - self.data["Close_1"].shift(1)
    ) / self.data["Close_1"].shift(1) - (
        self.data["Close_2"] - self.data["Close_2"].shift(1)
    ) / self.data["Close_2"].shift(1)
# Single asset trading
elif "Close" in self.data.columns:
    asset_returns = (
        self.data["Close"] - self.data["Close"].shift(1)
    ) / self.data["Close"].shift(1)
else:
    raise ValueError("Data does not contain required 'Close' columns")

portfolio = signals.with_columns([
    pl.col("positions"),
    asset_returns.alias("asset_returns"),
    (pl.col("positions").shift(1) * asset_returns).alias("strategy_returns"),
])

# Handle potential NaN or inf values
portfolio = portfolio.with_columns([
    pl.col("strategy_returns").replace({float("inf"): None, float("-inf"): None}).fill_null(0)
])

portfolio = portfolio.with_columns([
    (1 + pl.col("strategy_returns")).cum_prod().alias("cumulative_returns"),
    (self.initial_capital * (1 + pl.col("strategy_returns")).cum_prod()).alias("equity_curve"),
])
