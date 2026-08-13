import polars as pl

def to_pandas(self) -> pl.DataFrame:
    return self.__df.clone()
