import polars as pl

flg = pl.concat(flgs, how="horizontal").select(pl.concat_list(pl.all()).list.all().alias("flg")).to_series()
df = ds.filter(flg)