def merge_features(self) -> pl.LazyFrame:
    # ...
    if len(dfs) > 0:
        dfs = map(self._delete_filename_time_col, dfs)
        self.features = reduce(
            lambda left, right: left.join(right, on=["frame"], how="left"),
            dfs,
        )

        self.features = self.features.select(
            pl.lit(self.filename.as_posix()).alias("filename"),
            pl.col("frame").mul(1.0 / self.fps).alias("time"),
            pl.all(),
        )
    return self.features
