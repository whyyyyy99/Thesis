import polars as pl

input_df = input_df.with_row_index()
for d3_document_id in input_df["index"]:
    if d3_document_id == query_d3_document_id:
        continue
    pass
