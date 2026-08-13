import polars as pl
from ta.momentum import RSIIndicator

self.df = self.df.with_columns(
    pl.Series(
        "RSI",
        RSIIndicator(
            close=self.df["Close"].to_pandas(),
            window=window,
            fillna=fillna,
        ).rsi(),
    )
)
