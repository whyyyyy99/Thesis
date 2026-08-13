import polars as pl

df_cells = df_cells.sort(["x1", "x2", "y1", "y2"])
df_cells = df_cells.with_columns(
    pl.int_range(0, pl.len()).over(["x1", "x2", "y1"]).alias("cell_rk")
)
df_cells = df_cells.filter(pl.col("cell_rk") == 0)
