import polars as pl


class Dataset:
    def __init__(
        self,
        df: pl.DataFrame,
        x_columns: list[str],
        y_columns: list[str],
        w_columns: list[str],
    ) -> None:
        self.x_columns = x_columns
        self.y_columns = y_columns
        self.w_columns = w_columns
        self.__df = df.clone()
        self._validate(self.__df.columns, self.x_columns, self.y_columns, self.w_columns)

    @property
    def X(self) -> pl.DataFrame:
        return self.__df.select(self.x_columns).clone()

    @property
    def y(self) -> pl.DataFrame:
        return self.__df.select(self.y_columns).clone()

    @property
    def w(self) -> pl.DataFrame:
        return self.__df.select(self.w_columns).clone()

    def to_pandas(self) -> pl.DataFrame:
        return self.__df.clone()