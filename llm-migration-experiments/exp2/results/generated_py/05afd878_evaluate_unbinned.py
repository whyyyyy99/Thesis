import polars as pl

unbinned_otu_table = (
    unbinned_otu_table.groupby(["gene", "sequence"])
    .agg(
        pl.col("target").drop_nulls().first(),
        pl.col("taxonomy").drop_nulls().first(),
    )
    .sort(["gene", "sequence"])
)

unbinned_otu_table = unbinned_otu_table.drop_nulls()
unbinned_otu_table = unbinned_otu_table.with_columns(pl.col("target").cast(pl.Utf8))