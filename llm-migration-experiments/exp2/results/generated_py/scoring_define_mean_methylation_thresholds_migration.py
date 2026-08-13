import polars as pl

motif_binary_compare = motif_binary_compare.with_columns(
    pl.when(pl.col("methylation_binary") == 1)
    .then(
        pl.when(
            (pl.col("mean_methylation") - 4 * pl.col("std_methylation_bin")) < 0.1
        )
        .then(0.1)
        .otherwise(pl.col("mean_methylation") - 4 * pl.col("std_methylation_bin"))
    )
    .otherwise(pl.lit(float("nan")))
    .alias("methylation_mean_threshold")
).with_columns(
    pl.when(
        (pl.col("methylation_binary") == 1)
        & (
            (pl.col("mean") >= pl.col("methylation_mean_threshold"))
            | (pl.col("mean") > 0.4)
        )
    )
    .then(1)
    .otherwise(
        pl.when(pl.col("methylation_binary") == 1)
        .then(0)
        .otherwise(pl.lit(float("nan")))
    )
    .alias("methylation_binary_compare")
).with_columns(
    pl.when(pl.col("methylation_binary") == 0)
    .then(0.25)
    .otherwise(pl.col("methylation_mean_threshold"))
    .alias("methylation_mean_threshold")
).with_columns(
    pl.when(pl.col("methylation_binary") == 0)
    .then((pl.col("mean") >= 0.25).cast(pl.Int64))
    .otherwise(pl.col("methylation_binary_compare"))
    .alias("methylation_binary_compare")
)