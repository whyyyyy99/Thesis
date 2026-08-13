import polars as pl

self.documents_data.with_row_index("index").filter(
    pl.col("semanticscholar_url") == semanticscholar_url
).select("index").item()
