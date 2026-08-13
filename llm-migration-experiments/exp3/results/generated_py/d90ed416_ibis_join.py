import logging
import polars as pl

old_cluster = pl.read_csv(cluster, separator="\t")
comb_cluster = (
    new_cluster.select(["samples", "coassembly"])
    .join(old_cluster.select(["samples", "length"]), on="samples", how="inner")
)

if not comb_cluster.is_empty():
    comb_cluster.map_rows(lambda x: logging.warn(f"{x[1]} has been previously suggested"))
