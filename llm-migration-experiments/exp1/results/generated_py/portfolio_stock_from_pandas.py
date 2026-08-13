import polars as pl

ticker = yf.Ticker(name)
df = ticker.history(period=period, interval=interval)
df = pl.from_pandas(df, include_index=True)
index_col = df.columns[0]
if index_col != "Datetime":
    df = df.with_columns(pl.col(index_col).alias("Datetime")).drop(index_col)
return df
