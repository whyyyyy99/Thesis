import polars as pl

condition_adjacent = (
    (
        (pl.col("overlapping_y") > 5)
        & (
            pl.col("diff_x")
            / pl.max_horizontal(pl.col("width"), pl.col("width_"))
            <= 0.05
        )
    )
    | (
        (pl.col("overlapping_x") > 5)
        & (
            pl.col("diff_y")
            / pl.max_horizontal(pl.col("height"), pl.col("height_"))
            <= 0.05
        )
    )
)

df_cross_cells = df_cross_cells.with_columns(
    adjacent=condition_adjacent,
    redundant=pl.col("contained") & condition_adjacent,
)