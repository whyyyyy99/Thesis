import numpy as np
import polars as pl

def __update_indexing(self):
    lookup = self.get_lookup().clone()

    lookup = lookup.sort("row_index")
    n_rows = lookup.select(pl.col("row_index").is_not_null() & ~pl.col("row_index").is_nan()).sum().item()
    n_nan = len(lookup) - n_rows
    new_row_indices = list(range(n_rows))
    new_row_indices.extend(np.nan * np.ones(n_nan))
    lookup = lookup.with_columns(pl.Series("row_index", new_row_indices))

    lookup = lookup.sort("column_index")
    n_columns = lookup.select(pl.col("column_index").is_not_null() & ~pl.col("column_index").is_nan()).sum().item()
    n_nan = len(lookup) - n_columns
    new_column_indices = list(range(n_columns))
    new_column_indices.extend(np.nan * np.ones(n_nan))
    lookup = lookup.with_columns(pl.Series("column_index", new_column_indices))

    lookup = lookup.filter(
        ~(
            (pl.col("row_index").is_null() | pl.col("row_index").is_nan())
            & (pl.col("column_index").is_null() | pl.col("column_index").is_nan())
        )
    )
    if n_rows != self.matrix.shape[0]:
        raise ValueError(
            "The lookup must include row indices up to the length of the matrix."
        )
    if n_columns != self.matrix.shape[1]:
        raise ValueError(
            "The lookup must include column indices up to the length of the matrix."
        )
    self.lookup = lookup
    return