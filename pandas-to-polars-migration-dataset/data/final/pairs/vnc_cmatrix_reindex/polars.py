import polars as pl

    def __update_indexing(self):
        lookup = self.get_lookup()

        lookup = lookup.sort(by="row_index", nulls_last=True)
        n_rows = lookup["row_index"].count()
        n_null = len(lookup) - n_rows
        new_row_indices = list(range(n_rows)) + [None] * n_null
        lookup = lookup.with_columns(row_index=pl.Series(new_row_indices))

        lookup = lookup.sort(by="column_index", nulls_last=True)
        n_columns = lookup["column_index"].count()
        n_null = len(lookup) - n_columns
        new_column_indices = list(range(n_columns)) + [None] * n_null
        lookup = lookup.with_columns(column_index=pl.Series(new_column_indices))

        lookup = lookup.filter(
            ~pl.all_horizontal(pl.col("row_index", "column_index").is_null())
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
