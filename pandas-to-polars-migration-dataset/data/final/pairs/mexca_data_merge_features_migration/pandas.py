import pandas as pd

def merge_features(self) -> pd.DataFrame:
    # ...
    if len(dfs) > 0:
        dfs = map(self._delete_filename_time_col, dfs)
        self.features = reduce(
            lambda left, right: pd.merge(
                left, right, on=["frame"], how="left"
            ),
            dfs,
        )

        time = self.features.frame * (1 / self.fps)

        self.features.insert(0, "filename", self.filename)
        self.features.insert(1, "time", time)
    return self.features
