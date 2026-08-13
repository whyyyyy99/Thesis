import polars as pl

row_value_list: list[str] = df.filter(pl.col("index") == document_id_1).get_column(colname).to_list()
col_value_list: list[str] = df.filter(pl.col("index") == document_id_2).get_column(colname).to_list()