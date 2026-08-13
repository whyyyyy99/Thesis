import logging
import polars as pl

old_cluster = pl.read_csv(cluster, separator="\t")
comb_cluster = (
    new_cluster.select(["samples", "coassembly"])
    .join(old_cluster.select(["samples", "length"]), on="samples", how="inner")
)
if not comb_cluster.is_empty():
    for x in comb_cluster.iter_rows(named=True):
        logging.warn(f"{x['coassembly']} has been previously suggested")