import polars as pl

combined_otu_table = (
    recovered_otu_table.select(["coassembly", "gene", "sequence", "genome", "taxonomy"]).join(
        haystack_otu_table,
        on=["coassembly", "gene", "sequence"],
        how="full",
        coalesce=True,
        suffix="old",
    )
)
combined_otu_table = combined_otu_table.with_columns(
    pl.when(pl.col("taxonomy").is_not_null())
    .then(pl.col("taxonomy"))
    .otherwise(pl.col("taxonomyold"))
    .alias("taxonomy")
)
combined_otu_table = combined_otu_table.drop("taxonomyold")
combined_otu_table = combined_otu_table.filter(pl.col("coassembly").is_in(recovered_coassemblies))
combined_otu_table = combined_otu_table.filter(pl.col("genome").is_not_null() | pl.col("target").is_not_null())