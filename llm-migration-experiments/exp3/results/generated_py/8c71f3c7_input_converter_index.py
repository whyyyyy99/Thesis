self.documents_data.with_row_index("_index").filter(
    pl.col("semanticscholar_url") == semanticscholar_url
).get_column("_index").item()
