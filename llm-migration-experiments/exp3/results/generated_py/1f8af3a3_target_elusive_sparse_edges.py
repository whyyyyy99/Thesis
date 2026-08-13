import polars as pl

sparse_edges = (
    sample_pairs
    .group_by(["taxa_group", "sample_pairs"])
    .agg(
        pl.col("target").count().alias("weight"),
        pl.col("target").sort().str.join(",").alias("target_ids"),
    )
    .sort(["taxa_group", "sample_pairs"])
)
