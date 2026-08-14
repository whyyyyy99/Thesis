    sample_coassemblies = elusive_clusters.select(
        pl.col("samples").str.split(","),
        "coassembly"
    ).explode("samples")

    coassembly_edges = elusive_edges.with_columns(
        pl.col("sample1").str.replace(r"\.1$", ""),
        pl.col("sample2").str.replace(r"\.1$", ""),
    ).join(
        sample_coassemblies, left_on="sample1", right_on="samples", how="left"
    ).join(
        sample_coassemblies, left_on="sample2", right_on="samples", how="left", suffix="2"
    ).filter(
        pl.col("coassembly") == pl.col("coassembly2")
    ).with_columns(
        pl.col("target_ids").str.split(",").alias("target")
    ).explode("target"
    ).select(["target", "coassembly"]
    ).unique()
