import pandas as pd

        self.df['ROC'] = ROCIndicator(close=self.df.Close, window=window, fillna=fillna).roc()
