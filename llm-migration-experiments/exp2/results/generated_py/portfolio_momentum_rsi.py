import polars as pl

self.df = self.df.with_columns(
    pl.Series(
        "RSI",
        RSIIndicator(close=self.df["Close"], window=window, fillna=fillna).rsi(),
    )
)