import polars as pl

unbinned = unbinned.drop("found_in", strict=False)
groups = (
    unbinned.select(["gene", "sequence"])
    .unique(maintain_order=False)
    .sort(["gene", "sequence"])
    .with_row_index("target")
    .with_columns(pl.col("target").cast(pl.Utf8))
)
unbinned = unbinned.join(groups, on=["gene", "sequence"], how="left")
taxonomy = unbinned.group_by("target").agg(pl.col("taxonomy").first()).get_column("taxonomy")