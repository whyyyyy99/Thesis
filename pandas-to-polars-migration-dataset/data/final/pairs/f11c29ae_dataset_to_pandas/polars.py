    def to_frame(self) -> pl.DataFrame:
        return self.__df.clone()
