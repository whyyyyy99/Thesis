import pandas as pd

        stoch_rsi = StochRSIIndicator(
            close=self.df.Close, window=window, smooth1=smooth1, smooth2=smooth2, fillna=fillna
        )
        self.df['stoch_rsi'] = stoch_rsi.stochrsi()
        self.df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()
        self.df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
