import datetime

import polars as pl
import streamlit as st
import yfinance as yf


@st.cache_data
def load_yfinance_data_two_tickers(
    ticker1: str, ticker2: str, start_date: datetime.date, end_date: datetime.date
) -> pl.DataFrame:
    data1 = yf.download(ticker1, start=start_date, end=end_date)
    data2 = yf.download(ticker2, start=start_date, end=end_date)

    data1_pl = pl.from_pandas(data1.reset_index())
    data2_pl = pl.from_pandas(data2.reset_index())

    date_col1 = data1_pl.columns[0]
    date_col2 = data2_pl.columns[0]

    combined_data = (
        data1_pl.select([pl.col(date_col1), pl.col("Close").alias("Close_1")])
        .join(
            data2_pl.select([pl.col(date_col2), pl.col("Close").alias("Close_2")]),
            left_on=date_col1,
            right_on=date_col2,
            how="outer",
        )
        .sort(date_col1)
        .rename({date_col1: "Date"})
    )

    return combined_data.select(["Date", "Close_1", "Close_2"])