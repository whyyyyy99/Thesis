def to_csv(self, save_path: PathLike) -> None:
    """
    Save molecules as a csv file.

    Parameters
    ----------
    save_path : PathLike
        Save path.
    """
    return self.to_dataframe().write_csv(str(save_path))
