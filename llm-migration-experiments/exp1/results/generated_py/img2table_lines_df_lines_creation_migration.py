import polars as pl

df_lines = pl.DataFrame(data=[line.dict for line in lines])
df_lines = df_lines.with_columns(
    [
        pl.max_horizontal(pl.col("width"), pl.col("height")).alias("length"),
        (pl.col("x1") == pl.col("x2")).alias("vertical"),
        pl.Series("line_id", range(df_lines.height)),
    ]
)
df_lines = df_lines.select(
    [
        pl.col("x1").alias("x1_line"),
        pl.col("x2").alias("x2_line"),
        pl.col("y1").alias("y1_line"),
        pl.col("y2").alias("y2_line"),
        pl.col("width"),
        pl.col("height"),
        pl.col("length"),
        pl.col("vertical"),
        pl.col("line_id"),
    ]
)
