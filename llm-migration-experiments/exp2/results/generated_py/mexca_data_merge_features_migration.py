import polars as pl
from functools import reduce

def merge_features(self) -> pl.DataFrame:
    # ...
    if len(dfs) > 0:
        dfs = map(self._delete_filename_time_col, dfs)
        self.features = reduce(
            lambda left, right: left.join(right, on=["frame"], how="left"),
            dfs,
        )

        time = self.features["frame"] * (1 / self.fps)

        self.features = self.features.with_columns(
            [
                pl.lit(self.filename).alias("filename"),
                time.alias("time"),
            ]
        ).select(["filename", "time"] + [c for c in self.features.columns if c not in {"filename", "time"}])
    return self.features