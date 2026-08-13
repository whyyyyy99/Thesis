df_words = df_words.with_columns(
    [
        pl.Series("x1_bbox", bbox[0]),
        pl.Series("y1_bbox", bbox[1]),
        pl.Series("x2_bbox", bbox[2]),
        pl.Series("y2_bbox", bbox[3]),
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