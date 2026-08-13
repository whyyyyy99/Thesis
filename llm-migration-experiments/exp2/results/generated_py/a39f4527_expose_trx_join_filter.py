import polars as pl

trx_data = trx_data.join(date_lookup, on="pol_num", how="inner").filter(
    (pl.col("trx_date") >= date_cols[0]) & (pl.col("trx_date") <= date_cols[1])
).with_columns(pl.lit(1).alias("trx_n"))