import polars as pl

intersecting_lines = df_inter.filter((pl.col("intersection") / pl.col("length")) > 0.5)["line_id"].to_list()
