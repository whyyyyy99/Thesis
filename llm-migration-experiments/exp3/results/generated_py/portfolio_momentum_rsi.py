import polars as pl

self.df = self.df.with_columns(
    pl.when(
        pl.when(pl.col("Close").diff() < 0)
        .then(-pl.col("Close").diff())
        .otherwise(0.0)
        .ewm_mean(alpha=1 / window, adjust=False)
        == 0
    )
    .then(100.0)
    .otherwise(
        100.0
        - (
            100.0
            / (
                1.0
                + (
                    pl.when(pl.col("Close").diff() > 0)
                    .then(pl.col("Close").diff())
                    .otherwise(0.0)
                    .ewm_mean(alpha=1 / window, adjust=False)
                    / pl.when(pl.col("Close").diff() < 0)
                    .then(-pl.col("Close").diff())
                    .otherwise(0.0)
                    .ewm_mean(alpha=1 / window, adjust=False)
                )
            )
        )
    )
    .alias("RSI")
)
