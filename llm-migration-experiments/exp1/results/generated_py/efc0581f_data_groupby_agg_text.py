import polars as pl

df_text_parent = (
    df_words_contained.group_by("parent")
    .agg(
        [
            pl.col("x1").min().alias("x1"),
            pl.col("x2").max().alias("x2"),
            pl.col("y1").min().alias("y1"),
            pl.col("y2").max().alias("y2"),
            pl.col("value").implode().list.join(" ").alias("value"),
        ]
    )
    .sort(by=["y1", "x1"])
)
return "\n".join(map(str, df_text_parent.get_column("value").to_list())).strip() or None
