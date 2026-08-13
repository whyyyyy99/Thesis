import polars as pl

df = pl.from_pandas(summary_data.to_dataframe().reset_index())
df = df.filter(pl.col("name") == key).drop("name")
df = df.rename({"time": "Date", "realization": "Realization"})
df = df.select(["Realization", "Date", *[c for c in df.columns if c not in {"Realization", "Date"}]])
