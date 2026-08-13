import polars as pl

a = df.filter(pl.col("condition") == condition_a).get_column(metric).to_numpy()
b = df.filter(pl.col("condition") == condition_b).get_column(metric).to_numpy()