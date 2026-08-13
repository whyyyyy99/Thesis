import polars as pl
import numpy as np

def relocate(data: pl.DataFrame, x, before=None, after=None):
    x = np.atleast_1d(x)
    columns = data.columns
    columns2 = [c for c in columns if c not in x]
    if before is None and after is None:
        return data.select(list(x) + list(columns2))
    if before is None:
        pos = list(columns2).index(after) + 1
    else:
        pos = list(columns2).index(before)
    return data.select(list(columns2[:pos]) + list(x) + list(columns2[pos:]))
