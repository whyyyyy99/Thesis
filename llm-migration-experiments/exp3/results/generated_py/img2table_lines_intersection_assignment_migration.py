import polars as pl

df_w_l = df_w_l.with_columns(
    (
        pl.col("vertical").cast(pl.Int64) * vert_int
        + (1 - pl.col("vertical").cast(pl.Int64)) * hor_int
    ).alias("intersection")
)
