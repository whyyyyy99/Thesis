import polars as pl
import numpy as np

_index_col = "index"
if _index_col not in fp.columns:
    fp = fp.with_row_index(_index_col)
if _index_col not in network.columns:
    network = network.with_row_index(_index_col)

for id in fp.get_column(_index_col):
    nex_df = fp.filter(pl.col(_index_col) == id).select("toid")
    nex = nex_df.item(0, 0) if nex_df.height > 0 else None
    try:
        ds_wb_df = network.filter(pl.col(_index_col) == nex).select("toid")
        if ds_wb_df.height == 0:
            raise KeyError
        ds_wb = ds_wb_df.item(0, 0)
    except KeyError:
        continue
    sorter.add(ds_wb, id)
    # mutations:
    network = network.with_columns(
        pl.when(pl.col(_index_col) == nex)
        .then(pl.lit(ds_wb))
        .when(pl.col(_index_col) == ds_wb)
        .then(pl.lit(np.nan))
        .otherwise(pl.col("toid"))
        .alias("toid")
    )
    fp = fp.with_columns(
        pl.when(pl.col(_index_col) == ds_wb)
        .then(pl.lit(np.nan))
        .otherwise(pl.col("toid"))
        .alias("toid")
    )
