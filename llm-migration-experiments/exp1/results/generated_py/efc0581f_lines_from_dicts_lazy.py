import polars as pl

df_lines = pl.DataFrame([line.dict for line in lines])
df_lines = df_lines.with_columns(
    pl.max_horizontal(["width", "height"]).alias("length"),
    (pl.col("x1") == pl.col("x2")).alias("vertical"),
    pl.Series("line_id", range(len(df_lines))),
)
df_lines.columns = ['x1_line', 'x2_line', 'y1_line', 'y2_line', 'width', 'height', 'length', 'vertical', 'line_id']
