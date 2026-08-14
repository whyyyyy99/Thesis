def to_csv(self, save_path: str) -> None:
    """
    Save molecules as a csv file.

    Parameters
    ----------
    save_path : str
        Save path.
    """
    return self.to_dataframe().to_csv(save_path, index=False)
