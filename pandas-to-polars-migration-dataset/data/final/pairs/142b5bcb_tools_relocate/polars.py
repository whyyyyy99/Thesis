import polars as pl
import numpy as np

def relocate(data: pl.DataFrame, x: str | list | np.ndarray, before: str = None, after: str = None):
    assert before is None or after is None, \
        'One of `before` and `after` must be specified, but not both.'
    x = np.atleast_1d(x)
    columns = data.columns
    columns2 = [col for col in columns if col not in x]
    if before is None and after is None:
        return data.select(list(x) + columns2)
    if before is None:
        pos = list(columns2).index(after) + 1
    else:
        pos = list(columns2).index(before)
    return data.select(list(columns2[:pos]) + list(x) + list(columns2[pos:]))
