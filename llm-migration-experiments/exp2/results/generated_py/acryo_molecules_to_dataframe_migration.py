import numpy as np
import polars as pl

def to_dataframe(self) -> pl.DataFrame:
    rotvec = self.rotvec()
    data = np.concatenate([self.pos, rotvec], axis=1)
    df = pl.DataFrame(data, schema=_CSV_COLUMNS)
    if self._features is not None:
        df = pl.concat([df, pl.DataFrame(self._features)], how="horizontal")
    return df