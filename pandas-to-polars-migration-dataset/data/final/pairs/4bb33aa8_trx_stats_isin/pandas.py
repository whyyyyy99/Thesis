import pandas as pd

            assert all(pd.Series(by).isin(old_self.data.columns)), \
