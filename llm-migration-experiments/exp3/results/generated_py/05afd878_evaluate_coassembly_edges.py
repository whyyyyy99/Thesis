import re
import polars as pl

elusive_edges = elusive_edges.with_columns(
    pl.col("sample1").map_elements(lambda x: re.sub(r"\.1$", "", x), return_dtype=pl.Utf8),
    pl.col("sample2").map_elements(lambda x: re.sub(r"\.1$", "", x), return_dtype=pl.Utf8),
)

elusive_edges = (
    elusive_edges
    .join(elusive_clusters, on="sample1", how="left")
    .join(elusive_clusters, on="sample2", how="left", suffix="2")
)

coassembly_edges = elusive_edges.filter(
    pl.col("coassembly") == pl.col("coassembly2")
).clone()
coassembly_edges = coassembly_edges.with_columns(
    pl.col("target_ids").str.split(",").alias("target")
).explode("target").unique(
    subset=["target", "coassembly"],
    keep="first",
    maintain_order=True,
).select(["target", "coassembly"])
