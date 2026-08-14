import pandas as pd

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

        if not isinstance(lookup, pd.DataFrame):
            raise ValueError("The lookup must be a pandas dataframe.")

        lookup = lookup.copy()
        lookup["row_index"] = lookup["index"].values
        lookup["column_index"] = lookup["index"].values
        self.lookup = lookup.drop(columns="index")

        if not all(self.lookup["row_index"].isin(range(self.matrix.shape[0]))):
            raise ValueError(
                "The lookup must include row indices up to the length of the matrix."
            )
        if not all(self.lookup["column_index"].isin(range(self.matrix.shape[1]))):
            raise ValueError(
                "The lookup must include column indices up to the length of the matrix."
            )

        self.CR = CR or default_connectome_reader()
