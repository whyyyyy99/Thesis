import datetime

import polars as pl
import yfinance as yf


def load_yfinance_data_two_tickers(
    ticker1: str, ticker2: str, start_date: datetime.date, end_date: datetime.date
) -> pl.DataFrame:
    data1 = yf.download(ticker1, start=start_date, end=end_date)
    data2 = yf.download(ticker2, start=start_date, end=end_date)

    df1 = pl.from_pandas(data1.reset_index()).select(
        pl.col(data1.index.name or "Date").alias("date"), pl.col("Close").alias("Close_1")
    )
    df2 = pl.from_pandas(data2.reset_index()).select(
        pl.col(data2.index.name or "Date").alias("date"), pl.col("Close").alias("Close_2")
    )

    combined_data = (
        df1.join(df2, on="date", how="full", coalesce=True)
        .sort("date")
        .select(["Close_1", "Close_2"])
    )
    return combined_data
