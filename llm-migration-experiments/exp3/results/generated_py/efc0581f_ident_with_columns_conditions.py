import polars as pl

cross_h_lines = cross_h_lines.with_columns(
    (
        (pl.col("x1") - pl.col("x1_") / pl.col("width")).abs() <= 0.02
    ).alias("l_corresponds"),
    (
        (pl.col("x2") - pl.col("x2_") / pl.col("width")).abs() <= 0.02
    ).alias("r_corresponds"),
    (
        ((pl.col("x1") <= pl.col("x1_")) & (pl.col("x1_") <= pl.col("x2")))
        | ((pl.col("x1_") <= pl.col("x1")) & (pl.col("x1") <= pl.col("x2_")))
    ).alias("l_contained"),
    (
        ((pl.col("x1") <= pl.col("x2_")) & (pl.col("x2_") <= pl.col("x2")))
        | ((pl.col("x1_") <= pl.col("x2")) & (pl.col("x2") <= pl.col("x2_")))
    ).alias("r_contained"),
)
