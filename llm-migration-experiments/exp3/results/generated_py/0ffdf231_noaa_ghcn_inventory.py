import numpy as np
import pandas as pd
import polars as pl

inventory_df = pd.read_fwf(inventory_file, header=None, colspecs="infer", infer_nrows=np.inf)
inventory_df = pl.from_pandas(inventory_df)
inventory_df = inventory_df.select([inventory_df.columns[0], inventory_df.columns[4], inventory_df.columns[5]])
