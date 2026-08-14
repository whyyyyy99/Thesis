df_cells = (df_cells.with_columns([(pl.col('x2') - pl.col('x1')).alias('width'),
                                       (pl.col('y2') - pl.col('y1')).alias('height')])
                .with_columns((pl.col('height') * pl.col('width')).alias('area'))
                )
