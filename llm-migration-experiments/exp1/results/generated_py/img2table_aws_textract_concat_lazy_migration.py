import polars as pl

return OCRDataframe(df=pl.concat(list_dfs, how="vertical"))
