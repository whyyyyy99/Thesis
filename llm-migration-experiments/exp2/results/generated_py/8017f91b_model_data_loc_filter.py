import polars as pl

return (
    self.query_document,
    self.info_matrix[indices],
    self.integer_labels[indices],
    self.feature_matrix[indices],
)