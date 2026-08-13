import polars as pl

document_ids = df["document_id"].to_list()
titles = df["title"].to_list()
abstracts = df["abstract"].to_list()
