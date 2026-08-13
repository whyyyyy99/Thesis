import polars as pl

intersecting_lines = df_inter.filter(pl.col("intersection") / pl.col("length") > 0.5).get_column("line_id").to_list()
