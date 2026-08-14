    nontarget_otu_table = binned_otu_table.select([
        pl.col("sample").str.replace(r"\.1$", ""),
        "gene", "sequence", "taxonomy", "found_in"
    ]).join(
        sample_coassemblies, left_on="sample", right_on="samples", how="left"
    ).drop("sample"
    ).drop_nulls("coassembly"
    ).unique(
    ).with_columns(
        pl.lit(None).cast(str).alias("target")
    )

    haystack_otu_table = pl.concat([elusive_otu_table, nontarget_otu_table])
