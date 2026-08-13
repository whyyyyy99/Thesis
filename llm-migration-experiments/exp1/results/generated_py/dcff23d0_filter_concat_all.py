import polars as pl

flg = pl.concat(flgs, how="horizontal").select(pl.all_horizontal()).to_series()
df = ds.filter(flg)
