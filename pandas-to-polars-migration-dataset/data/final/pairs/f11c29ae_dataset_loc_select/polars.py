    def X(self) -> pl.DataFrame:
        return self.__df.select(self.x_columns).clone()
    def y(self) -> pl.DataFrame:
        return self.__df.select(self.y_columns).clone()
    def w(self) -> pl.DataFrame:
        return self.__df.select(self.w_columns).clone()
