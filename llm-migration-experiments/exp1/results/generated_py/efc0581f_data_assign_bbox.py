import polars as pl

df_words = df_words.with_columns(
    [
        pl.lit(bbox[0]).alias("x1_bbox"),
        pl.lit(bbox[1]).alias("y1_bbox"),
        pl.lit(bbox[2]).alias("x2_bbox"),
        pl.lit(bbox[3]).alias("y2_bbox"),
    ]
)

df_words = df_words.with_columns(
    [
        pl.max_horizontal("x1", "x1_bbox").alias("x_left"),
        pl.max_horizontal("y1", "y1_bbox").alias("y_top"),
        pl.min_horizontal("x2", "x2_bbox").alias("x_right"),
        pl.min_horizontal("y2", "y2_bbox").alias("y_bottom"),
    ]
)
