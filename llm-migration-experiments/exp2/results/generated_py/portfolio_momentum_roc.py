import polars as pl

self.df = self.df.with_columns(
    (
        ((self.df["Close"] / self.df["Close"].shift(window)) - 1) * 100
    ).fill_null(0).alias("ROC")
    if fillna
    else (
        ((self.df["Close"] / self.df["Close"].shift(window)) - 1) * 100
    ).alias("ROC")
)