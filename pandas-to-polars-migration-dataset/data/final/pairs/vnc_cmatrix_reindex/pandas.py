import pandas as pd

    def __update_indexing(self):
        lookup = self.get_lookup().copy()

        lookup.sort_values(by="row_index", inplace=True)
        n_rows = lookup["row_index"].count()
        n_nan = len(lookup) - n_rows
        new_row_indices = list(range(n_rows))
        new_row_indices.extend(np.nan * np.ones(n_nan))
        lookup["row_index"] = new_row_indices

        lookup = lookup.sort_values(by="column_index")
        n_columns = lookup["column_index"].count()
        n_nan = len(lookup) - n_columns
        new_column_indices = list(range(n_columns))
        new_column_indices.extend(np.nan * np.ones(n_nan))
        lookup["column_index"] = new_column_indices

        lookup.dropna(
            axis="index",
            subset=["row_index", "column_index"],
            how="all",
            inplace=True,
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
