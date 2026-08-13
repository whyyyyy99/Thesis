import polars as pl

def _loc_by_label(df: pl.DataFrame, row_label, colname):
    if "document_id" in df.columns:
        filtered = df.filter(pl.col("document_id") == row_label)
    elif "index" in df.columns:
        filtered = df.filter(pl.col("index") == row_label)
    else:
        filtered = df.filter(pl.col(df.columns[0]) == row_label)

    if isinstance(colname, str):
        return filtered.get_column(colname).to_list()

    return list(filtered.select(colname).row(0)) if filtered.height > 0 else []

row_value_list: list[str] = _loc_by_label(df, document_id_1, colname)
col_value_list: list[str] = _loc_by_label(df, document_id_2, colname)
