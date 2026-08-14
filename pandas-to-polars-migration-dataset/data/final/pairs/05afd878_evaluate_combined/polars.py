    combined_otu_table = recovered_otu_table.join(
        haystack_otu_table, on=["coassembly", "gene", "sequence"], how="outer", suffix="old"
    ).select(
        "coassembly", "gene", "sequence", "genome", "target", "found_in",
        pl.when(pl.col("taxonomy").is_null())
        .then(pl.col("taxonomyold"))
        .otherwise(pl.col("taxonomy"))
        .alias("taxonomy"),
    ).filter(
        (pl.col("coassembly").is_in(pl.lit(recovered_otu_table["coassembly"]))) &
        ((pl.col("genome").is_not_null()) | (pl.col("target").is_not_null()))
    )
