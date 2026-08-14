df_cross_cells = (df_cells.join(df_cells_cp, how='cross')
                      .filter(pl.col('index') != pl.col('index_'))
                      .filter(pl.col('area') <= pl.col('area_'))
                      )
