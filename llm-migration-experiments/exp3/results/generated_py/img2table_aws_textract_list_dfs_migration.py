import polars as pl

list_dfs = map(pl.DataFrame, content)
