import polars as pl

_DATAFRAME_ATTRS = {}

def preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    processed_df = df.clone()
    processed_df.columns = cleaned_columns

    _DATAFRAME_ATTRS[id(processed_df)] = {
        "original_columns": original_columns,
        "column_mapping": dict(zip(cleaned_columns, original_columns)),
    }

    logger.info("DataFrame preprocessing completed successfully")
    logger.debug(
        f"Column mapping created: {len(_DATAFRAME_ATTRS[id(processed_df)]['column_mapping'])} entries"
    )

    return processed_df


def get_original_column_name(df: pl.DataFrame, cleaned_name: str) -> str:
    if id(df) in _DATAFRAME_ATTRS and "column_mapping" in _DATAFRAME_ATTRS[id(df)]:
        original_name = _DATAFRAME_ATTRS[id(df)]["column_mapping"].get(
            cleaned_name, cleaned_name
        )
        if original_name != cleaned_name:
            logger.debug(
                f"Retrieved original column name: '{cleaned_name}' -> '{original_name}'"
            )
        return original_name

    logger.debug(f"No column mapping found, returning cleaned name: '{cleaned_name}'")
    return cleaned_name
