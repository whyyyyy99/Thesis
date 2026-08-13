import polars as pl

sparse_edges = (
    sample_pairs.group_by(["taxa_group", "sample_pairs"], maintain_order=False)
    .agg(
        pl.col("target").count().alias("count"),
        pl.col("target").sort().list.join(",").alias("<lambda_0>"),
    )
    .sort(["taxa_group", "sample_pairs"])
)

sparse_edges = sparse_edges.rename({"count": "weight", "<lambda_0>": "target_ids"})