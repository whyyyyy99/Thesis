import polars as pl

df_inter = (
    df_w_l.group_by(["line_id", "length"])
    .agg(pl.col("intersection").sum().alias("intersection"))
    .sort(["line_id", "length"])
)

intersecting_lines = (
    df_inter.filter(pl.col("intersection") / pl.col("length") > 0.5)
    .get_column("line_id")
    .to_list()
)