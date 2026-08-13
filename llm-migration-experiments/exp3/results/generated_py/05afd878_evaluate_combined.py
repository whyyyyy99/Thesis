import polars as pl

combined_otu_table = (
    recovered_otu_table.join(
        haystack_otu_table,
        on=["coassembly", "gene", "sequence"],
        how="full",
        suffix="old",
    )
    .with_columns(
        pl.when(pl.col("taxonomy").is_not_null())
        .then(pl.col("taxonomy"))
        .otherwise(pl.col("taxonomyold"))
        .alias("taxonomy")
    )
    .drop("taxonomyold")
    .sort(["coassembly", "gene", "sequence"])
)

combined_otu_table = combined_otu_table.filter(pl.col("coassembly").is_in(recovered_coassemblies))
combined_otu_table = combined_otu_table.filter(
    pl.col("genome").is_not_null() | pl.col("target").is_not_null()
)
