import polars as pl

if "found_in" in unbinned.columns:
    unbinned = unbinned.drop("found_in")

_group_keys = (
    unbinned.select(["gene", "sequence"])
    .unique()
    .sort(["gene", "sequence"])
    .with_row_index("target")
)

unbinned = unbinned.join(_group_keys, on=["gene", "sequence"], how="left")
unbinned = unbinned.with_columns(pl.col("target").cast(pl.Utf8))

taxonomy = (
    unbinned.group_by("target")
    .agg(pl.col("taxonomy").drop_nulls().first().alias("taxonomy"))
    .sort("target")
)
