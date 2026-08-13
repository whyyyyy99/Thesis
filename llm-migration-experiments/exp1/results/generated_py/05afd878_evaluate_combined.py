import polars as pl

combined_otu_table = (
    recovered_otu_table.join(haystack_otu_table, on=["coassembly", "gene", "sequence"], how="outer", suffix="old")
    .with_columns(
        pl.coalesce([pl.col("taxonomy").fill_nan(None), pl.col("taxonomyold")]).alias("taxonomy")
    )
    .drop("taxonomyold")
)

combined_otu_table = combined_otu_table.filter(pl.col("coassembly").is_in(recovered_coassemblies))
combined_otu_table = combined_otu_table.filter(pl.col("genome").is_not_null() | pl.col("target").is_not_null())
