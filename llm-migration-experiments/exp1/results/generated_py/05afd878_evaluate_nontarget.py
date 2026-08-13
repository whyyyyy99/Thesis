import polars as pl
import re

binned_otu_table = binned_otu_table.with_columns(
    pl.col("sample").map_elements(lambda x: re.sub(r"\.1$", "", x), return_dtype=pl.Utf8)
)

nontarget_otu_table = (
    binned_otu_table
    .select(["sample", "gene", "sequence", "taxonomy", "found_in"])
    .join(elusive_clusters, on="sample")
    .drop_nulls(subset=["coassembly"])
    .unique(maintain_order=True)
)

nontarget_otu_table = nontarget_otu_table.with_columns(pl.lit(None).alias("target"))

haystack_otu_table = pl.concat([elusive_otu_table, nontarget_otu_table], how="diagonal")
