import polars as pl

df_text_parent = (
    df_words_contained.group_by("parent")
    .agg(
        x1=pl.col("x1").min(),
        x2=pl.col("x2").max(),
        y1=pl.col("y1").min(),
        y2=pl.col("y2").max(),
        value=pl.col("value"),
    )
    .with_columns(value=pl.col("value").list.join(" "))
    .sort(["y1", "x1"])
)

if df_text_parent.height == 0:
    return None

return df_text_parent["value"].cast(pl.Utf8).str.concat(delimiter="\n").strip() or None