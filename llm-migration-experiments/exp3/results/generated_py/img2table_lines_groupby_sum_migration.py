import polars as pl

df_inter = (
    df_w_l.group_by(["line_id", "length"])
    .agg(pl.col("intersection").sum())
    .sort(["line_id", "length"])
)
