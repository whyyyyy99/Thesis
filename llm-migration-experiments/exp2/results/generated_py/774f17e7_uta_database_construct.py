import polars as pl

return pl.DataFrame(
    results, schema=["pro_ac", "tx_ac", "alt_ac", "cds_start_i"]
).unique()
