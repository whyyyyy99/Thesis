import polars as pl

df = pl.concat([pl.from_pandas(ds.to_pandas()) for ds in ds_list])
