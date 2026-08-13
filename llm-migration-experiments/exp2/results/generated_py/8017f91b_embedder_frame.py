import polars as pl

return pl.DataFrame(
    {
        "document_id": list(embeddings_mapping.keys()),
        "embedding": list(embeddings_mapping.values()),
    }
)