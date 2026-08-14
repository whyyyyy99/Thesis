df_words_lines = df_words_lines.with_columns((pl.col('vertical').cast(pl.Int8) * vert_int
                                                  + (1 - pl.col('vertical').cast(pl.Int8) * hor_int)).alias('intersection')
                                                 )
