import polars as pl

data = data.with_columns(pl.col("claims").alias("n_claims"))