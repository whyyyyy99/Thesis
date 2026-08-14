import pandas as pd

def write_df_to_pickle(
    df: pd.DataFrame,
    path: Path,
) -> None:
    """Write a Pandas DataFrame to a pickle file."""
    df.to_pickle(path)

def load_df_from_pickle(path: Path) -> pd.DataFrame:
    """Load a Pandas DataFrame from a pickle file."""
    return pd.read_pickle(path)
