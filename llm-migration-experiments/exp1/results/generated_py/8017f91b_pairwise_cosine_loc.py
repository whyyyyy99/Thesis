import polars as pl

row_embedding: EmbeddingVector = df.filter(pl.col("index") == document_id_1).select(pl.exclude("index")).to_series(0).item()
col_embedding: EmbeddingVector = df.filter(pl.col("index") == document_id_2).select(pl.exclude("index")).to_series(0).item()
