df_cross_cells = (df_cross_cells
                  .with_columns([(pl.col('x_right') - pl.col('x_left')).alias('overlapping_x'),
                                 (pl.col('y_bottom') - pl.col('y_top')).alias('overlapping_y')])
                  .with_columns(pl.min([(pl.col(_1) - pl.col(_2)).abs()
                                        for _1, _2 in itertools.product(['x1', 'x2'], ['x1_', 'x2_'])]
                                       ).alias('diff_x'))
                  .with_columns(pl.min([(pl.col(_1) - pl.col(_2)).abs()
                                        for _1, _2 in itertools.product(['y1', 'y2'], ['y1_', 'y2_'])]
                                       ).alias('diff_y'))
                  )
