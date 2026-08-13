import polars as pl
import numpy as np

fp = fp.with_row_index("__index__")
network = network.with_row_index("__index__")

_fp_index_to_pos = {v: i for i, v in enumerate(fp["__index__"].to_list())}
_network_index_to_pos = {v: i for i, v in enumerate(network["__index__"].to_list())}

_fp_toid = fp["toid"].to_list()
_network_toid = network["toid"].to_list()

for id in fp["__index__"].to_list():
    nex = _fp_toid[_fp_index_to_pos[id]]
    try:
        ds_wb = _network_toid[_network_index_to_pos[nex]]
    except KeyError:
        continue
    sorter.add(ds_wb, id)
    _network_toid[_network_index_to_pos[nex]] = ds_wb
    _network_toid[_network_index_to_pos[ds_wb]] = None
    _fp_toid[_fp_index_to_pos[ds_wb]] = None

fp = fp.drop("__index__").with_columns(pl.Series("toid", _fp_toid))
network = network.drop("__index__").with_columns(pl.Series("toid", _network_toid))
