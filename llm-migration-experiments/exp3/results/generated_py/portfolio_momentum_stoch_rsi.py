import polars as pl

stoch_rsi = StochRSIIndicator(
    close=self.df["Close"], window=window, smooth1=smooth1, smooth2=smooth2, fillna=fillna
)
self.df = self.df.with_columns(
    [
        pl.Series("stoch_rsi", stoch_rsi.stochrsi()),
        pl.Series("stoch_rsi_d", stoch_rsi.stochrsi_d()),
        pl.Series("stoch_rsi_k", stoch_rsi.stochrsi_k()),
    ]
)
