import re
import polars as pl

binned_otu_table = binned_otu_table.with_columns(
    pl.col("sample").str.replace(r"\.1$", "").alias("sample")
)

nontarget_otu_table = (
    binned_otu_table
    .join(elusive_clusters, on="sample", how="left")
    .drop_nulls(subset=["coassembly"])
    .unique()
)
nontarget_otu_table = nontarget_otu_table.with_columns(pl.lit(None).alias("target"))

haystack_otu_table = pl.concat([elusive_otu_table, nontarget_otu_table])
