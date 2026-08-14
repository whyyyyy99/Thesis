import polars as pl

def get_cells_dataframe(horizontal_lines: List[Line], vertical_lines: List[Line]) -> pl.LazyFrame:
    default_df = pl.DataFrame(columns=["x1", "x2", "y1", "y2", 'width', "height"]).lazy()
    df_h_lines = pl.from_dicts([l.dict for l in horizontal_lines]).lazy() if horizontal_lines else default_df.clone()
    df_v_lines = pl.from_dicts([l.dict for l in vertical_lines]).lazy() if vertical_lines else default_df.clone()

    df_h_lines_cp = (df_h_lines.clone()
                     .rename({col: f"{col}_" for col in df_h_lines.columns})
                     )

    cross_h_lines = (df_h_lines.join(df_h_lines_cp, how='cross')
                     .filter(pl.col('y1') < pl.col('y1_'))
                     )

    cross_h_lines = cross_h_lines.with_columns([
        (((pl.col('x1') - pl.col('x1_')) / pl.col('width')).abs() <= 0.02).alias("l_corresponds"),
        (((pl.col('x2') - pl.col('x2_')) / pl.col('width')).abs() <= 0.02).alias("r_corresponds"),
        (((pl.col('x1') <= pl.col('x1_')) & (pl.col('x1_') <= pl.col('x2')))
         | ((pl.col('x1_') <= pl.col('x1')) & (pl.col('x1') <= pl.col('x2_')))).alias('l_contained'),
        (((pl.col('x1') <= pl.col('x2_')) & (pl.col('x2_') <= pl.col('x2')))
         | ((pl.col('x1_') <= pl.col('x2')) & (pl.col('x2') <= pl.col('x2_')))).alias('r_contained')
    ])

    matching_condition = ((pl.col('l_corresponds') | pl.col('l_contained'))
                          & (pl.col('r_corresponds') | pl.col('r_contained')))
    cross_h_lines = cross_h_lines.filter(matching_condition)

    df_bbox = (cross_h_lines.select([pl.max([pl.col('x1'), pl.col('x1_')]).alias('x1_bbox'),
                                     pl.min([pl.col('x2'), pl.col('x2_')]).alias('x2_bbox'),
                                     pl.col('y1').alias("y1_bbox"),
                                     pl.col('y1_').alias('y2_bbox')]
                                    )
               .with_row_count(name="idx")
               )

    df_bbox = df_bbox.with_columns(pl.max([(pl.col('x2_bbox') - pl.col('x1_bbox')) * 0.05,
                                           pl.lit(5.0)]).round(0).alias('h_margin')
                                   )
    df_bbox_v = df_bbox.join(df_v_lines, how='cross')

    horizontal_cond = ((pl.col("x1_bbox") - pl.col("h_margin") <= pl.col("x1"))
                       & (pl.col("x2_bbox") + pl.col("h_margin") >= pl.col("x1")))
    df_bbox_v = df_bbox_v.filter(horizontal_cond)

    df_bbox_v = (df_bbox_v.with_columns((pl.min([pl.col('y2'), pl.col('y2_bbox')])
                                         - pl.max([pl.col('y1'), pl.col('y1_bbox')])).alias('overlapping')
                                        )
                 .filter(pl.col('overlapping') / (pl.col('y2_bbox') - pl.col('y1_bbox')) >= 0.8)
                 )

    df_bbox_delimiters = (df_bbox_v.sort(['idx', "x1_bbox", "x2_bbox", "y1_bbox", "y2_bbox", "x1"])
                          .groupby(['idx', "x1_bbox", "x2_bbox", "y1_bbox", "y2_bbox"])
                          .agg(pl.col('x1').list().alias('dels'))
                          .filter(pl.col("dels").arr.lengths() >= 2)
                          )

    df_cells = (df_bbox_delimiters.explode("dels")
                .with_columns([pl.col('dels').shift(1).over(pl.col('idx')).alias("x1_bbox"),
                               pl.col('dels').alias("x2_bbox")])
                .filter(pl.col('x1_bbox').is_not_null())
                .select([pl.col("x1_bbox").alias("x1"),
                         pl.col("y1_bbox").alias("y1"),
                         pl.col("x2_bbox").alias("x2"),
                         pl.col("y2_bbox").alias("y2")
                         ])
                .sort(['x1', 'y1', 'x2', 'y2'])
                .with_row_count(name="index")
                )

    return df_cells
