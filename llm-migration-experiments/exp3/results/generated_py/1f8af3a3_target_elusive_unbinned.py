import polars as pl

unbinned = unbinned.drop("found_in", strict=False)
group_keys = (
    unbinned.select(["gene", "sequence"])
    .unique(maintain_order=False)
    .sort(["gene", "sequence"])
    .with_row_index("target")
    .select(["gene", "sequence", "target"])
)

unbinned = unbinned.join(group_keys, on=["gene", "sequence"], how="left")
unbinned = unbinned.with_columns(pl.col("target").cast(pl.Utf8))

taxonomy = (
    unbinned.group_by("target")
    .agg(pl.col("taxonomy").first().alias("taxonomy"))
    .sort("target")
)
