import polars as pl


@staticmethod
def _delete_filename_time_col(df: pl.DataFrame) -> pl.DataFrame:
    if "time" in df.columns:
        df = df.drop("time", strict=False)
    if "filename" in df.columns:
        df = df.drop("filename", strict=False)
    return df