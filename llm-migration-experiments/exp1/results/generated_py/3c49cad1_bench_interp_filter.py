import polars as pl

filtered_df = df.filter(pl.col("date").cast(pl.Utf8) == day_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
values = filtered_df["value"].to_list()
