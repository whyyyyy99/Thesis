import polars as pl

        df_words = self.df.filter(pl.col('class') == "ocrx_word")
        if page_number:
            df_words = df_words.filter(pl.col('page') == page_number)
        df_words = df_words.filter(pl.col('value').is_not_null() & (pl.col('confidence') >= min_confidence))

        list_cells = [{"row": id_row, "col": id_col, "x1_w": cell.x1, "x2_w": cell.x2, "y1_w": cell.y1, "y2_w": cell.y2}
                      for id_row, row in enumerate(table.items)
                      for id_col, cell in enumerate(row.items)]
        df_cells = pl.from_dicts(dicts=list_cells).lazy()

        df_word_cells = df_words.join(other=df_cells, how="cross")

        df_word_cells = df_word_cells.with_columns([
            pl.max([pl.col('x1'), pl.col('x1_w')]).alias('x_left'),
            pl.max([pl.col('y1'), pl.col('y1_w')]).alias('y_top'),
            pl.min([pl.col('x2'), pl.col('x2_w')]).alias('x_right'),
            pl.min([pl.col('y2'), pl.col('y2_w')]).alias('y_bottom'),
        ])

        df_intersection = (df_word_cells.filter(pl.col("x_right") > pl.col("x_left"))
                           .filter(pl.col("y_bottom") > pl.col("y_top")))

        df_text_parent = (df_intersection
                          .groupby(['row', 'col', 'parent'])
                          .agg([pl.col('value').apply(lambda x: ' '.join(x)).alias('value')])
                          .sort([pl.col("row"), pl.col("col"), pl.col('y1'), pl.col('x1')])
                          .groupby(['row', 'col'])
                          .agg(pl.col('value').apply(lambda x: '\n'.join(x).strip()).alias('text')))
