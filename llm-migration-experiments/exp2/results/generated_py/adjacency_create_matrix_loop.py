import polars as pl
import numpy as np

for id in fp.get_column("index").to_list():
    fp_match = fp.filter(pl.col("index") == id)
    nex = fp_match.get_column("toid")[0]

    try:
        network_match = network.filter(pl.col("index") == nex)
        if network_match.height == 0:
            raise KeyError(nex)
        ds_wb = network_match.get_column("toid")[0]
    except KeyError:
        continue

    sorter.add(ds_wb, id)

    network = network.with_columns(
        pl.when(pl.col("index") == nex)
        .then(pl.lit(ds_wb))
        .otherwise(pl.col("toid"))
        .alias("toid")
    )
    network = network.with_columns(
        pl.when(pl.col("index") == ds_wb)
        .then(pl.lit(np.nan))
        .otherwise(pl.col("toid"))
        .alias("toid")
    )
    fp = fp.with_columns(
        pl.when(pl.col("index") == ds_wb)
        .then(pl.lit(np.nan))
        .otherwise(pl.col("toid"))
        .alias("toid")
    )