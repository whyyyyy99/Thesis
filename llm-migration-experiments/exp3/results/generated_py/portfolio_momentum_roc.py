import polars as pl

self.df = self.df.with_columns(
    (
        (pl.col("Close") / pl.col("Close").shift(window) - 1) * 100
    ).fill_null(0 if fillna else None).alias("ROC")
)
