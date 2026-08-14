    df_lines = (pl.from_dicts(dicts=[line.dict for line in lines])
                .lazy()
                .with_columns([pl.max([pl.col('width'), pl.col('height')]).alias('length'),
                               (pl.col('x1') == pl.col('x2')).alias('vertical')])
                .with_row_count(name="line_id")
                .rename({"x1": "x1_line", "x2": "x2_line", "y1": "y1_line", "y2": "y2_line"})
                )
