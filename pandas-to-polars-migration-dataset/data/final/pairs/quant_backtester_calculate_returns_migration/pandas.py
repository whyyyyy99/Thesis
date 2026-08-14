import pandas as pd

portfolio = pd.DataFrame(index=signals.index)
portfolio["positions"] = signals["positions"]

# Pairs trading
if "Close_1" in self.data.columns and "Close_2" in self.data.columns:
    portfolio["asset_returns"] = (
        self.data["Close_1"].pct_change() - self.data["Close_2"].pct_change()
    )
# Single asset trading
elif "Close" in self.data.columns:
    portfolio["asset_returns"] = self.data["Close"].pct_change()
else:
    raise ValueError("Data does not contain required 'Close' columns")

portfolio["strategy_returns"] = (
    portfolio["positions"].shift(1) * portfolio["asset_returns"]
)
# Handle potential NaN or inf values
portfolio["strategy_returns"] = (
    portfolio["strategy_returns"].replace([np.inf, -np.inf], np.nan).fillna(0)
)
portfolio["cumulative_returns"] = (1 + portfolio["strategy_returns"]).cumprod()
portfolio["equity_curve"] = (
    self.initial_capital * portfolio["cumulative_returns"]
)
