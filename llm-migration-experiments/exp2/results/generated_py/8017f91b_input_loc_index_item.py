import polars as pl

self.documents_data.with_row_index("_idx").filter(
    pl.col("semanticscholar_url") == semanticscholar_url
).get_column("_idx").item()