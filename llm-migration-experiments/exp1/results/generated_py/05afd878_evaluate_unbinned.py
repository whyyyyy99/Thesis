import polars as pl

unbinned_otu_table = (
    unbinned_otu_table.group_by(["gene", "sequence"]).agg(pl.all().first()).select(
        ["gene", "sequence", "target", "taxonomy"]
    )
)
unbinned_otu_table = unbinned_otu_table.drop_nulls()
unbinned_otu_table = unbinned_otu_table.with_columns(pl.col("target").cast(pl.Utf8))
