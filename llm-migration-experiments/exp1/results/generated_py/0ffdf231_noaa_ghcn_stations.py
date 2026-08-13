import numpy as np
import pandas as pd
import polars as pl

df = pd.read_fwf(
    listings_file,
    dtype=str,
    header=None,
    colspecs="infer",
    infer_nrows=np.inf,
)
df = pl.from_pandas(df)
df = df[:, [0, 1, 2, 3, 4, 5, 8]]
