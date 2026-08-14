df_inter = (df_words_lines.groupby(['line_id', 'length'])
                .agg(pl.sum(pl.col('intersection')).alias('intersection'))
                )
