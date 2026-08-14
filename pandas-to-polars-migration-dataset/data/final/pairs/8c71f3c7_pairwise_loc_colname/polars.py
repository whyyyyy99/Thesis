        row_value_list: list[str] = (
            df.filter(pl.col("document_id") == document_id_1).select(colname).item()
        )
        col_value_list: list[str] = (
            df.filter(pl.col("document_id") == document_id_2).select(colname).item()
        )
