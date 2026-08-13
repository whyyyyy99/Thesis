import polars as pl

total_amount = len(df["value"])
zero_amount = len(df.filter(pl.col("value") == 0.0))
