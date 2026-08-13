import polars as pl

ticker = yf.Ticker(name)
df = ticker.history(period=period, interval=interval).reset_index()
df = pl.from_pandas(df).with_columns(Datetime=pl.col(df.columns[0])).drop(df.columns[0])
return df
