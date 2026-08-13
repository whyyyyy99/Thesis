import polars as pl

low_min = self.df["Low"].rolling_min(window_size=window)
high_max = self.df["High"].rolling_max(window_size=window)

stoch = 100 * (self.df["Close"] - low_min) / (high_max - low_min)
stoch_signal = stoch.rolling_mean(window_size=smooth_window)

if fillna:
    stoch = stoch.fill_null(0)
    stoch_signal = stoch_signal.fill_null(0)

self.df = self.df.with_columns(
    [
        stoch.alias("stoch"),
        stoch_signal.alias("stoch_signal"),
    ]
)
