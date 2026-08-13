import polars as pl

input_df.with_row_index(name="document_id").select("document_id")
