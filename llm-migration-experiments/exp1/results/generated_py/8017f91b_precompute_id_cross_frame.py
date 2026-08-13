import polars as pl

for d3_document_id in input_df.get_column("index"):
    if d3_document_id == query_d3_document_id:
        continue
    ...
