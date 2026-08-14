    ticker = yf.Ticker(name)
    df = ticker.history(period=period, interval=interval)
    # Convert pandas DataFrame to polars DataFrame
    pl_df = pl.from_pandas(df)
    pl_df = pl_df.with_columns(pl.col("index").alias("Datetime"))
    return pl_df
