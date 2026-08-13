import polars as pl

self.df = self.df.with_columns(
    (
        (
            pl.col("Close") - pl.col("Close").shift(window)
        )
        / pl.col("Close").shift(window)
        * 100
    )
    .fill_null(0)
    .alias("ROC")
    if fillna
    else (
        (
            pl.col("Close") - pl.col("Close").shift(window)
        )
        / pl.col("Close").shift(window)
        * 100
    ).alias("ROC")
)
