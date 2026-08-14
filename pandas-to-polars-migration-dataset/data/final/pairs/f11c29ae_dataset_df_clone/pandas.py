import pandas as pd

class Dataset:
    def __init__(
        self,
        df: pd.DataFrame,
        x_columns: list[str],
        y_columns: list[str],
        w_columns: list[str],
    ) -> None:
        self.x_columns = x_columns
        self.y_columns = y_columns
        self.w_columns = w_columns
        self.__df = df.copy()
        self._validate(
            self.__df.columns.to_list(), self.x_columns, self.y_columns, self.w_columns
        )

    @property
    def X(self) -> pd.DataFrame:
        return self.__df.loc[:, self.x_columns].copy()

    @property
    def y(self) -> pd.DataFrame:
        return self.__df.loc[:, self.y_columns].copy()

    @property
    def w(self) -> pd.DataFrame:
        return self.__df.loc[:, self.w_columns].copy()

    def to_pandas(self) -> pd.DataFrame:
        return self.__df.copy()
