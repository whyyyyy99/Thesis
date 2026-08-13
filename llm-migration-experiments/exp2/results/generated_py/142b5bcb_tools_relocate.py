import pandas as pd
import numpy as np
import polars as pl

def relocate(data: pl.DataFrame, x, before=None, after=None):
    x = np.atleast_1d(x).tolist()
    columns = data.columns
    columns2 = [c for c in columns if c not in x]
    if before is None and after is None:
        return data.select(x + columns2)
    if before is None:
        pos = columns2.index(after) + 1
    else:
        pos = columns2.index(before)
    return data.select(columns2[:pos] + x + columns2[pos:])