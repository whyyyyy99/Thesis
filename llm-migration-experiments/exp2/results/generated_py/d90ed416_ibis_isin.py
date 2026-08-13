import os
import polars as pl

elusive_clusters = pl.read_csv(os.path.abspath(args.elusive_clusters), separator="\t")
elusive_clusters = elusive_clusters.filter(pl.col("coassembly").is_in(args.coassemblies))