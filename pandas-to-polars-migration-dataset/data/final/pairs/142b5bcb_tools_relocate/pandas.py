import pandas as pd
import numpy as np

def relocate(data: pd.DataFrame, x, before=None, after=None):
    x = np.atleast_1d(x)
    columns = data.columns
    columns2 = columns[~columns.isin(x)]
    if before is None and after is None:
        return data[list(x) + list(columns2)]
    if before is None:
        pos = list(columns2).index(after) + 1
    else:
        pos = list(columns2).index(before)
    return data[list(columns2[:pos]) + list(x) + list(columns2[pos:])]
