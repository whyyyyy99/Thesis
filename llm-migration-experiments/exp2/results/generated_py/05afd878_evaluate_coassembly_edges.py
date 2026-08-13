import re
import polars as pl

elusive_edges["sample1"] = elusive_edges["sample1"].str.replace(r"\.1$", "")
elusive_edges["sample2"] = elusive_edges["sample2"].str.replace(r"\.1$", "")
elusive_edges = (
    elusive_edges.join(elusive_clusters, on="sample1")
    .join(elusive_clusters, left_on="sample2", right_on="sample2", suffix="2")
)
coassembly_edges = elusive_edges.filter(pl.col("coassembly") == pl.col("coassembly2")).clone()
coassembly_edges = coassembly_edges.with_columns(pl.col("target_ids").str.split(",").alias("target"))
coassembly_edges = coassembly_edges.explode("target").unique(subset=["target", "coassembly"], keep="first", maintain_order=True)
coassembly_edges = coassembly_edges.select(["target", "coassembly"])