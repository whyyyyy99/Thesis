    sparse_edges = sample_pairs.groupby([
        "taxa_group", "sample", "sample_2"
    ]).agg([
        pl.count().alias("weight").cast(int),
        pl.col("target").sort().str.concat(",").alias("target_ids")
    ]).select([
        "taxa_group", "weight", "target_ids",
        pl.col("sample").alias("sample1"),
        pl.col("sample_2").alias("sample2")
    ])
