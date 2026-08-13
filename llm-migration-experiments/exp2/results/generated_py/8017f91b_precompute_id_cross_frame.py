import polars as pl

for d3_document_id in (input_df["index"] if "index" in input_df.columns else range(input_df.height)):
    if d3_document_id == query_d3_document_id:
        continue
    ...