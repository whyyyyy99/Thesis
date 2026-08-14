import pandas as pd

@st.cache_data
def load_yfinance_data_two_tickers(
    ticker1: str, ticker2: str, start_date: datetime.date, end_date: datetime.date
) -> pd.DataFrame:
    data1 = yf.download(ticker1, start=start_date, end=end_date)
    data2 = yf.download(ticker2, start=start_date, end=end_date)
    combined_data = pd.DataFrame({"Close_1": data1["Close"], "Close_2": data2["Close"]})
    return combined_data
