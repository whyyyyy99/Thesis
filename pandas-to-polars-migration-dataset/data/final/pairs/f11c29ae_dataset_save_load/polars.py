import polars as pl

    def save(self, path: Path) -> None:
        if path.exists():
            rmtree(path)
        path.mkdir(exist_ok=True, parents=True)
        self.__df.write_parquet(path / "data.parquet")
        with shelve.open(path / "meta.shelve") as shelf:
            shelf["x_columns"] = self.x_columns
            shelf["y_columns"] = self.y_columns
            shelf["w_columns"] = self.w_columns

    @classmethod
    def load(cls, path: Path) -> Dataset:
        data_path = path / "data.parquet"
        meta_path = path / "meta.json"
        if (not data_path.exists()) or (not meta_path.exists()):
            raise FileNotFoundError()

        df = pl.read_parquet(data_path)
        meta = shelve.open(path / "meta.shelve")
        return cls(df, **meta)
