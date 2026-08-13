import polars as pl

copy_df = copy_df.with_columns(
    pl.col("tx_ac")
    .str.split(".")
    .list.get(0)
    .str.split("NM_")
    .list.get(1)
    .cast(pl.Int64)
    .alias("ac_no_version_as_int"),
    pl.col("tx_ac")
    .str.split(".")
    .list.get(1)
    .alias("ac_version"),
)
copy_df = copy_df.sort(
    ["ac_no_version_as_int", "ac_version"], descending=[True, True]
)