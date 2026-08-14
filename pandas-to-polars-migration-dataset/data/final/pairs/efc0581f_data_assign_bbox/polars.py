        df_words = (df_words.with_columns([pl.lit(bbox[0]).alias('x1_bbox'),
                                           pl.lit(bbox[1]).alias('y1_bbox'),
                                           pl.lit(bbox[2]).alias('x2_bbox'),
                                           pl.lit(bbox[3]).alias('y2_bbox')])
                    .with_columns([pl.max([pl.col('x1'), pl.col('x1_bbox')]).alias('x_left'),
                                   pl.max([pl.col('y1'), pl.col('y1_bbox')]).alias('y_top'),
                                   pl.min([pl.col('x2'), pl.col('x2_bbox')]).alias('x_right'),
                                   pl.min([pl.col('y2'), pl.col('y2_bbox')]).alias('y_bottom'),
                                   ])
                    )
