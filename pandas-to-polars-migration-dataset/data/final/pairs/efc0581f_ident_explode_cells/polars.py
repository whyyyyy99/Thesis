    df_cells = (df_bbox_delimiters.explode("dels")
                .with_columns([pl.col('dels').shift(1).over(pl.col('idx')).alias("x1_bbox"),
                               pl.col('dels').alias("x2_bbox")])
                .filter(pl.col('x1_bbox').is_not_null())
                .select([pl.col("x1_bbox").alias("x1"),
                         pl.col("y1_bbox").alias("y1"),
                         pl.col("x2_bbox").alias("x2"),
                         pl.col("y2_bbox").alias("y2")])
                .sort(['x1', 'y1', 'x2', 'y2'])
                .with_row_count(name="index")
                )
    return df_cells
