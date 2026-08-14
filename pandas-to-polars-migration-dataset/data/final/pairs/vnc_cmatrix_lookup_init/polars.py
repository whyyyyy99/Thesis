import polars as pl

    def __init__(
        self,
        matrix: sc.sparse.csr_matrix,
        lookup: pl.DataFrame,
        CR: ConnectomeReader | None = None,
    ):
        if not sc.sparse.issparse(matrix):
            matrix = sc.sparse.csr_matrix(matrix)
        if not isinstance(matrix, sc.sparse.csr_matrix):
            matrix = matrix.tocsr()
        self.matrix = matrix

        if not isinstance(lookup, pl.DataFrame):
            raise ValueError("The lookup must be a polars dataframe.")

        self.lookup = lookup.with_columns(
            row_index=pl.col("index"),
            column_index=pl.col("index"),
        ).drop("index")

        if not all(self.lookup["row_index"].is_in(range(self.matrix.shape[0]))):
            raise ValueError(
                "The lookup must include row indices up to the length of the matrix."
            )
        if not all(self.lookup["column_index"].is_in(range(self.matrix.shape[1]))):
            raise ValueError(
                "The lookup must include column indices up to the length of the matrix."
            )

        self.CR = CR or default_connectome_reader()
