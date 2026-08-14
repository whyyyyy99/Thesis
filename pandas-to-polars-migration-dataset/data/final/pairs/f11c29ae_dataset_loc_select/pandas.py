import pandas as pd

    def X(self) -> pd.DataFrame:
        return self.__df.loc[:, self.x_columns].copy()
    def y(self) -> pd.DataFrame:
        return self.__df.loc[:, self.y_columns].copy()
    def w(self) -> pd.DataFrame:
        return self.__df.loc[:, self.w_columns].copy()
