def to_dataframe(self) -> pd.DataFrame:
    import pandas as pd
    rotvec = self.rotvec()
    data = np.concatenate([self.pos, rotvec], axis=1)
    df = pd.DataFrame(data, columns=_CSV_COLUMNS)
    if self._features is not None:
        df = pd.concat([df, self._features], axis=1)
    return df
