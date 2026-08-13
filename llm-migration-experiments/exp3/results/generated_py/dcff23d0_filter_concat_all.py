import polars as pl

flg = pl.concat(flgs, how="horizontal").select(pl.all_horizontal(pl.all())).to_series()
df = ds.filter(flg)
