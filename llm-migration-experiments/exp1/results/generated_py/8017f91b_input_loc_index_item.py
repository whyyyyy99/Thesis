import polars as pl

self.documents_data.with_row_index("__index").filter(
    pl.col("semanticscholar_url") == semanticscholar_url
).select("__index").item()
