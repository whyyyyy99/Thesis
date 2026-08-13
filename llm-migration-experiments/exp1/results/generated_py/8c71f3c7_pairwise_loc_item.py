import polars as pl

row_embedding: EmbeddingVector = df.filter(pl.col("document_id") == document_id_1).select(pl.all()).to_series().item()
col_embedding: EmbeddingVector = df.filter(pl.col("document_id") == document_id_2).select(pl.all()).to_series().item()
