import polars as pl

total_amount = len(df["value"])
zero_amount = df.filter(pl.col("value") == 0.0).height
