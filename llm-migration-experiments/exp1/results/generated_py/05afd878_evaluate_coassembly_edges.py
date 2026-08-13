import polars as pl

elusive_edges = elusive_edges.with_columns(
    [
        pl.col("sample1").str.replace(r"\.1$", ""),
        pl.col("sample2").str.replace(r"\.1$", ""),
    ]
)

elusive_edges = (
    elusive_edges
    .join(elusive_clusters, left_on="sample1", right_on="sample1", how="left")
    .join(elusive_clusters, left_on="sample2", right_on="sample2", how="left", suffix="2")
)

coassembly_edges = elusive_edges.filter(
    pl.col("coassembly") == pl.col("coassembly2")
).clone()

coassembly_edges = (
    coassembly_edges
    .with_columns(pl.col("target_ids").str.split(",").alias("target"))
    .explode("target")
    .unique(subset=["target", "coassembly"])
    .select(["target", "coassembly"])
)
