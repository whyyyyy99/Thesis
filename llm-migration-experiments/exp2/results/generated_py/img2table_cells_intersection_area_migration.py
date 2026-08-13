import polars as pl

df_cross_cells = df_cross_cells.with_columns(
    (
        (pl.col("x_right") - pl.col("x_left"))
        * (pl.col("y_bottom") - pl.col("y_top"))
    ).alias("int_area")
)