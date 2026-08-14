import polars as pl

_column_mapping_registry: Dict[int, Dict] = {}

def preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.height} rows, {df.width} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    column_mapping = dict(zip(original_columns, cleaned_columns))
    processed_df = df.rename(column_mapping)

    _column_mapping_registry[id(processed_df)] = {
        "original_columns": original_columns,
        "column_mapping": dict(zip(cleaned_columns, original_columns)),
    }

    logger.info("DataFrame preprocessing completed successfully")
    logger.debug(
        f"Column mapping created: {len(column_mapping)} entries"
    )

    return processed_df

def get_original_column_name(df: pl.DataFrame, cleaned_name: str) -> str:
    df_id = id(df)
    if df_id in _column_mapping_registry and "column_mapping" in _column_mapping_registry[df_id]:
        original_name = _column_mapping_registry[df_id]["column_mapping"].get(cleaned_name, cleaned_name)
        if original_name != cleaned_name:
            logger.debug(
                f"Retrieved original column name: '{cleaned_name}' -> '{original_name}'"
            )
        return original_name

    logger.debug(f"No column mapping found, returning cleaned name: '{cleaned_name}'")
    return cleaned_name
