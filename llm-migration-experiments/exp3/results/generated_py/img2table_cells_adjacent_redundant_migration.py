condition_adjacent = (((df_cross_cells["overlapping_y"] > 5)
                       & (df_cross_cells["diff_x"] / pl.max_horizontal("width", "width_") <= 0.05))
                      | ((df_cross_cells["overlapping_x"] > 5)
                         & (df_cross_cells["diff_y"] / pl.max_horizontal("height", "height_") <= 0.05))
                      )
df_cross_cells = df_cross_cells.with_columns([
    condition_adjacent.alias("adjacent"),
    (pl.col("contained") & condition_adjacent).alias("redundant"),
])
