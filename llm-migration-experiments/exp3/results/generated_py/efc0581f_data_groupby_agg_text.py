import polars as pl

df_text_parent = (
    df_words_contained.group_by("parent")
    .agg(
        x1=pl.col("x1").min(),
        x2=pl.col("x2").max(),
        y1=pl.col("y1").min(),
        y2=pl.col("y2").max(),
        value=pl.col("value").cast(pl.Utf8).str.join(" "),
    )
    .sort(by=["y1", "x1"])
)

if df_text_parent.height == 0:
    return None

result = df_text_parent.get_column("value").cast(pl.Utf8).str.join("\n").strip_chars()
return result if result != "" else None
