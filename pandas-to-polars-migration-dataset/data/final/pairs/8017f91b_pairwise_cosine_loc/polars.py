        row_embedding: EmbeddingVector = (
            df.filter(pl.col("d3_document_id") == document_id_1).select("embedding").item()
        )
        col_embedding: EmbeddingVector = (
            df.filter(pl.col("d3_document_id") == document_id_2).select("embedding").item()
        )
