import polars as pl

row_value_list: list[str] = df.filter(pl.col("document_id") == document_id_1).select(colname).to_series().to_list()
col_value_list: list[str] = df.filter(pl.col("document_id") == document_id_2).select(colname).to_series().to_list()
