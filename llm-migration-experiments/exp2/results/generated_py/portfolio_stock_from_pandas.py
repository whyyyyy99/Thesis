import pandas as pd
import polars as pl

ticker = yf.Ticker(name)
df = ticker.history(period=period, interval=interval)
df = pl.from_pandas(df, include_index=True).rename({"index": "Datetime"})
df = df.select([c for c in df.columns if c != "Datetime"] + ["Datetime"])
return df