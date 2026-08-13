import polars as pl

df = summary_data.to_dataframe()
df = df.xs(key, level="name").reset_index()
df = pl.from_pandas(df).rename({"time": "Date", "realization": "Realization"})
df = df.select(["Realization", "Date", *[c for c in df.columns if c not in {"Realization", "Date"}]])