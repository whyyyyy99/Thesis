import polars as pl

df = pl.read_json(response).lazy()
