    sample_pairs = unbinned.join(unbinned, how="cross", suffix="_2"
    ).filter(
        (pl.col("target") == pl.col("target_2")) &
        (pl.col("sample").str.encode("hex") < pl.col("sample_2").str.encode("hex")) &
        (pl.col("coverage") + pl.col("coverage_2") > MIN_COASSEMBLY_COVERAGE)
    ).with_columns(
        pl.col("taxonomy").str.split(TAXA_LEVEL_SEP).arr.get(TAXA_LEVEL_OF_INTEREST).alias("taxa_group"),
    ).filter(
        (pl.col("taxa_group").is_not_null()) &
        ((TAXA_OF_INTEREST == "") |
        (pl.col("taxa_group") == TAXA_OF_INTEREST))
    )
