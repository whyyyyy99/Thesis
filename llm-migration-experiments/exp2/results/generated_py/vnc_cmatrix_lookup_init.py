import pandas as pd
import polars as pl

    def __init__(
        self,
        matrix: sc.sparse.csr_matrix,
        lookup: pd.DataFrame,
        CR: ConnectomeReader | None = None,
    ):
        if not sc.sparse.issparse(matrix):
            matrix = sc.sparse.csr_matrix(matrix)
        if not isinstance(matrix, sc.sparse.csr_matrix):
            matrix = matrix.tocsr()
        self.matrix = matrix

        if not isinstance(lookup, pl.DataFrame):
            raise ValueError("The lookup must be a pandas dataframe.")

        lookup = lookup.clone()
        lookup = lookup.with_columns(
            pl.col("index").alias("row_index"),
            pl.col("index").alias("column_index"),
        )
        self.lookup = lookup.drop("index")

        if not self.lookup.get_column("row_index").is_in(range(self.matrix.shape[0])).all():
            raise ValueError(
                "The lookup must include row indices up to the length of the matrix."
            )
        if not self.lookup.get_column("column_index").is_in(range(self.matrix.shape[1])).all():
            raise ValueError(
                "The lookup must include column indices up to the length of the matrix."
            )

        self.CR = CR or default_connectome_reader()