import polars as pl

df = pl.read_csv(response)
return df.rename(GEOSPHERE_RENAME_MAP).drop(["Sonnenschein", "Globalstrahlung"])