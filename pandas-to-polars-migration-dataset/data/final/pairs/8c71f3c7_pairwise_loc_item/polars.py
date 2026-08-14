        row_embedding: EmbeddingVector = df.filter(pl.col("document_id") == document_id_1).item()
        col_embedding: EmbeddingVector = df.filter(pl.col("document_id") == document_id_2).item()
