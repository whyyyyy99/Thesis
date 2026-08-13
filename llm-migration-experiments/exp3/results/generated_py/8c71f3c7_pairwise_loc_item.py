import polars as pl

_index_col = "index" if "index" in df.columns else df.columns[0]

row_embedding: EmbeddingVector = (
    df.filter(pl.col(_index_col) == document_id_1)
    .select(pl.exclude(_index_col))
    .to_series(0)
    .item()
)
col_embedding: EmbeddingVector = (
    df.filter(pl.col(_index_col) == document_id_2)
    .select(pl.exclude(_index_col))
    .to_series(0)
    .item()
)
