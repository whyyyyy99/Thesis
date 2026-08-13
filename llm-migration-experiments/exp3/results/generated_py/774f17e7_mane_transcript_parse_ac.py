copy_df = copy_df.with_columns(
    [
        pl.col("tx_ac")
        .str.split(".")
        .list.first()
        .str.split("NM_")
        .list.get(1)
        .cast(pl.Int64)
        .alias("ac_no_version_as_int"),
        pl.col("tx_ac")
        .str.split(".")
        .list.get(1)
        .alias("ac_version"),
    ]
).sort(
    ["ac_no_version_as_int", "ac_version"],
    descending=[True, True],
)
