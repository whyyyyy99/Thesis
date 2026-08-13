stoch_rsi = StochRSIIndicator(
    close=self.df["Close"], window=window, smooth1=smooth1, smooth2=smooth2, fillna=fillna
)
self.df = self.df.with_columns(
    [
        stoch_rsi.stochrsi().alias("stoch_rsi"),
        stoch_rsi.stochrsi_d().alias("stoch_rsi_d"),
        stoch_rsi.stochrsi_k().alias("stoch_rsi_k"),
    ]
)
