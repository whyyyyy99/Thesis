import polars as pl


def to_csv(self, save_path: str) -> None:
    """
    Save molecules as a csv file.

    Parameters
    ----------
    save_path : str
        Save path.
    """
    return self.to_dataframe().write_csv(save_path)
