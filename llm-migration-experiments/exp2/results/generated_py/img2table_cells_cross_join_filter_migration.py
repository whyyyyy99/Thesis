df_cross_cells = df_cells.with_row_index("index").join(df_cells_cp, how="cross")
df_cross_cells = df_cross_cells.filter(pl.col("index") != pl.col("index_"))
df_cross_cells = df_cross_cells.filter(pl.col("area") <= pl.col("area_"))