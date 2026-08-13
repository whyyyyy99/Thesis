import polars as pl

df = pl.from_pandas(summary_data.to_dataframe())
if "name" in df.columns:
    df = df.filter(pl.col("name") == key).drop("name")
if "time" in df.columns:
    df = df.rename({"time": "Date"})
if "realization" in df.columns:
    df = df.rename({"realization": "Realization"})
if "Realization" in df.columns and "Date" in df.columns:
    df = df.select(["Realization", "Date"] + [c for c in df.columns if c not in {"Realization", "Date"}])
