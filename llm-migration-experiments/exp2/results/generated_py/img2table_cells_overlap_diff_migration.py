import polars as pl

df_cross_cells = df_cross_cells.with_columns(
    [
        (pl.col("x_right") - pl.col("x_left")).alias("overlapping_x"),
        (pl.col("y_bottom") - pl.col("y_top")).alias("overlapping_y"),
        pl.min_horizontal(
            [
                (pl.col("x2") - pl.col("x1_")).abs(),
                (pl.col("x1") - pl.col("x2_")).abs(),
                (pl.col("x1") - pl.col("x1_")).abs(),
                (pl.col("x2") - pl.col("x2_")).abs(),
            ]
        ).alias("diff_x"),
        pl.min_horizontal(
            [
                (pl.col("y1") - pl.col("y1_")).abs(),
                (pl.col("y2") - pl.col("y1_")).abs(),
                (pl.col("y1") - pl.col("y2_")).abs(),
                (pl.col("y2") - pl.col("y2_")).abs(),
            ]
        ).alias("diff_y"),
    ]
)