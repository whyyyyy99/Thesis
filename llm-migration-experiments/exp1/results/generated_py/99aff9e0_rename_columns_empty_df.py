import polars as pl

df = pl.DataFrame(schema=[(col, pl.Null) for col in df.columns])
