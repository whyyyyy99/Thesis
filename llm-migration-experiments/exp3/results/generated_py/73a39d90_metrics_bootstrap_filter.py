import polars as pl

a = df.filter(pl.col("condition") == condition_a).select(metric).to_series().to_numpy()
b = df.filter(pl.col("condition") == condition_b).select(metric).to_series().to_numpy()
