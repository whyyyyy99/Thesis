        df_text_parent = (df_words_contained
                          .groupby('parent')
                          .agg([pl.col('x1').min(),
                                pl.col('x2').max(),
                                pl.col('y1').min(),
                                pl.col('y2').max(),
                                pl.col('value').list()])
                          .sort([pl.col("y1"), pl.col("x1")]))
        text_lines = (df_text_parent.select(pl.col('value'))
                      .collect()
                      .get_column('value')
                      .to_list())
        return "\n".join([" ".join(line).strip() for line in text_lines]).strip() or None
