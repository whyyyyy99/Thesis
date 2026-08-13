vert_int = (
    (
        ((pl.col("x1_line") > pl.col("x1")) & (pl.col("x1_line") < pl.col("x2"))).cast(pl.Int64)
        * (pl.min_horizontal(pl.col("y2"), pl.col("y2_line")) - pl.max_horizontal(pl.col("y1"), pl.col("y1_line"))).clip(lower_bound=0)
    )
)

hor_int = (
    (
        ((pl.col("y1_line") > pl.col("y1")) & (pl.col("y1_line") < pl.col("y2"))).cast(pl.Int64)
        * (pl.min_horizontal(pl.col("x2"), pl.col("x2_line")) - pl.max_horizontal(pl.col("x1"), pl.col("x1_line"))).clip(lower_bound=0)
    )
)