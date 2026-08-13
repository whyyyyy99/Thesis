import polars as pl

trx_data = (
    trx_data.join(date_lookup, how="inner", on="pol_num")
    .filter((pl.col("trx_date") >= date_cols[0]) & (pl.col("trx_date") <= date_cols[1]))
)
trx_data = trx_data.with_columns(pl.lit(1).alias("trx_n"))
