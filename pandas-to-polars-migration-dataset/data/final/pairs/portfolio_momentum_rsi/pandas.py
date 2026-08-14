import pandas as pd

        self.df['RSI'] = RSIIndicator(close=self.df.Close, window=window, fillna=fillna).rsi()
