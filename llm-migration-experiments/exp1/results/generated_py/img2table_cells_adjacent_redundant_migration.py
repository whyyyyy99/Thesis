import polars as pl

condition_adjacent = (
    (
        (df_cross_cells["overlapping_y"] > 5)
        & (
            df_cross_cells["diff_x"]
            / pl.max_horizontal(df_cross_cells["width"], df_cross_cells["width_"])
            <= 0.05
        )
    )
    | (
        (df_cross_cells["overlapping_x"] > 5)
        & (
            df_cross_cells["diff_y"]
            / pl.max_horizontal(df_cross_cells["height"], df_cross_cells["height_"])
            <= 0.05
        )
    )
)
df_cross_cells = df_cross_cells.with_columns(
    adjacent=condition_adjacent,
    redundant=pl.col("contained") & pl.col("adjacent"),
)
