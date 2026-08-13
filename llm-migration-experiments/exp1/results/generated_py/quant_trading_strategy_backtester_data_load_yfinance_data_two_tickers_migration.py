import datetime

import polars as pl

@st.cache_data
def load_yfinance_data_two_tickers(
    ticker1: str, ticker2: str, start_date: datetime.date, end_date: datetime.date
) -> pl.DataFrame:
    data1 = yf.download(ticker1, start=start_date, end=end_date)
    data2 = yf.download(ticker2, start=start_date, end=end_date)

    combined_data = (
        pl.DataFrame(
            {
                "Date": data1.index,
                "Close_1": data1["Close"].to_list(),
            }
        )
        .join(
            pl.DataFrame(
                {
                    "Date": data2.index,
                    "Close_2": data2["Close"].to_list(),
                }
            ),
            on="Date",
            how="outer",
        )
        .select(["Close_1", "Close_2"])
    )
    return combined_data
