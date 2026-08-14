import pandas as pd

@staticmethod
def _delete_filename_time_col(df: pd.DataFrame) -> pd.DataFrame:
    if "time" in df.columns:
        del df["time"]
    if "filename" in df.columns:
        del df["filename"]
    return df
