import polars as pl

delta = self.df["Close"].diff()
gain = delta.clip(lower_bound=0)
loss = (-delta).clip(lower_bound=0)

avg_gain = gain.ewm_mean(alpha=1 / window, adjust=False, min_periods=window)
avg_loss = loss.ewm_mean(alpha=1 / window, adjust=False, min_periods=window)

rs = avg_gain / avg_loss
rsi = pl.when(avg_loss == 0).then(100.0).otherwise(100 - (100 / (1 + rs)))

rsi_min = rsi.rolling_min(window_size=window, min_periods=window)
rsi_max = rsi.rolling_max(window_size=window, min_periods=window)

stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min)
stoch_rsi_k = stoch_rsi.rolling_mean(window_size=smooth1, min_periods=smooth1)
stoch_rsi_d = stoch_rsi_k.rolling_mean(window_size=smooth2, min_periods=smooth2)

if fillna:
    stoch_rsi = stoch_rsi.fill_null(0)
    stoch_rsi_d = stoch_rsi_d.fill_null(0)
    stoch_rsi_k = stoch_rsi_k.fill_null(0)

self.df = self.df.with_columns(
    stoch_rsi.alias("stoch_rsi"),
    stoch_rsi_d.alias("stoch_rsi_d"),
    stoch_rsi_k.alias("stoch_rsi_k"),
)