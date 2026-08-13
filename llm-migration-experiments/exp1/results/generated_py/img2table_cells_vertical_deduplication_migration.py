import polars as pl

df_cells = df_cells.sort(by=["x1", "x2", "y1", "y2"])
df_cells = df_cells.with_columns(pl.cum_count().over(["x1", "x2", "y1"]).alias("cell_rk") - 1)
df_cells = df_cells.filter(pl.col("cell_rk") == 0)
df_cells = df_cells.sort(by=["x1", "x2", "y2", "y1"], descending=[False, False, False, True])
df_cells = df_cells.with_columns(pl.cum_count().over(["x1", "x2", "y2"]).alias("cell_rk") - 1)
df_cells = df_cells.filter(pl.col("cell_rk") == 0)
