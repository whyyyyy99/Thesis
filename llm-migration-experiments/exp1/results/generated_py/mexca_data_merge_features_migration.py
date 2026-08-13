import polars as pl
from functools import reduce

def merge_features(self) -> pl.DataFrame:
    # ...
    if len(dfs) > 0:
        dfs = map(self._delete_filename_time_col, dfs)
        self.features = reduce(
            lambda left, right: left.join(right, on="frame", how="left"),
            dfs,
        )

        time = self.features["frame"] * (1 / self.fps)

        self.features = self.features.insert_column(
            0, pl.Series("filename", [self.filename] * self.features.height)
        )
        self.features = self.features.insert_column(1, pl.Series("time", time))
    return self.features
