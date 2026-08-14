@staticmethod
def _delete_filename_time_col(df: pl.LazyFrame) -> pl.LazyFrame:
    if "time" in df.columns:
        df = df.drop("time")
    if "filename" in df.columns:
        df = df.drop("filename")
    return df
