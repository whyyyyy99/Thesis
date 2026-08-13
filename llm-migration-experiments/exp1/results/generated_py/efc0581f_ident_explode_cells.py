import polars as pl

try:
    df_bbox_delimiters = (
        df_bbox_delimiters.filter(pl.col("dels").is_not_null())
        .explode("dels")
        .with_row_index("index")
        .with_columns(
            [
                pl.col("dels").list.get(0).alias("del1"),
                pl.col("dels").list.get(1).alias("del2"),
            ]
        )
        .with_columns(
            [
                pl.col("del1").alias("x1_bbox"),
                pl.col("del2").alias("x2_bbox"),
            ]
        )
    )
    df_cells = df_bbox_delimiters.select(["x1_bbox", "y1_bbox", "x2_bbox", "y2_bbox"])
    df_cells = df_cells.rename(
        {"x1_bbox": "x1", "y1_bbox": "y1", "x2_bbox": "x2", "y2_bbox": "y2"}
    )
    return df_cells.with_columns(pl.Series("index", range(df_cells.height))).select(
        ["index", "x1", "y1", "x2", "y2"]
    )
except ValueError:
    return pl.DataFrame({"index": [], "x1": [], "y1": [], "x2": [], "y2": []})
