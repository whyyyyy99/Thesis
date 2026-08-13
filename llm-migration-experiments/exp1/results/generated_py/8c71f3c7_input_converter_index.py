import polars as pl

self.documents_data.with_row_index().filter(
    pl.col("semanticscholar_url") == semanticscholar_url
).get_column("index").item()
