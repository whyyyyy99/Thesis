def to_dataframe(self) -> pl.DataFrame:
    import polars as pl
    rotvec = self.rotvec()
    data = np.concatenate([self.pos, rotvec], axis=1)
    df = pl.DataFrame(data, columns=_CSV_COLUMNS)
    if self._features is not None:
        df = df.with_columns(list(self._features))
    return df
