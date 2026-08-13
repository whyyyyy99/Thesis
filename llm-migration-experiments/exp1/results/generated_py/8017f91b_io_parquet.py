import pickle
from pathlib import Path

import pandas as pd
import polars as pl


def write_df_to_pickle(
    df: pl.DataFrame,
    path: Path,
) -> None:
    """Write a Pandas DataFrame to a pickle file."""
    with open(path, "wb") as file:
        pickle.dump(df, file)


def load_df_from_pickle(path: Path) -> pl.DataFrame:
    """Load a Pandas DataFrame from a pickle file."""
    obj = pd.read_pickle(path)
    if isinstance(obj, pd.DataFrame):
        return pl.from_pandas(obj)
    return obj
