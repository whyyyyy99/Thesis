import pandas as pd

    def to_pandas(self) -> pd.DataFrame:
        return self.__df.copy()
