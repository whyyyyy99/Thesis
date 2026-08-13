import polars as pd

            self.query_document,
            self.info_matrix.take(indices),
            self.integer_labels.take(indices),
            self.cosine_similarity_ranks.take(indices),
