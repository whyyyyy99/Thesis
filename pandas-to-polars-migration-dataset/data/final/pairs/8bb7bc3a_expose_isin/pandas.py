import pandas as pd

            assert all(pd.Series(by).isin(self.data.columns)), \
