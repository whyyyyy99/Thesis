@st.cache_data
def load_yfinance_data_two_tickers(
    ticker1: str, ticker2: str, start_date: datetime.date, end_date: datetime.date
) -> pl.DataFrame:
    data1 = yf.download(ticker1, start=start_date, end=end_date)
    data2 = yf.download(ticker2, start=start_date, end=end_date)
    pl_data1 = pl.from_pandas(data1.reset_index()[["Date", "Close"]])
    pl_data2 = pl.from_pandas(data2.reset_index()[["Date", "Close"]])
    pl_data1 = pl_data1.rename({"Close": "Close_1"})
    pl_data2 = pl_data2.rename({"Close": "Close_2"})
    combined_data = pl_data1.join(pl_data2, on="Date", how="outer")
    return combined_data
