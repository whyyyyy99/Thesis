import polars as pl

_df_column_mapping = {}

def preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    processed_df = df.clone()
    processed_df.columns = cleaned_columns

    column_mapping = dict(zip(cleaned_columns, original_columns))
    _df_column_mapping[id(processed_df)] = column_mapping
    try:
        processed_df.attrs = {"original_columns": original_columns, "column_mapping": column_mapping}
    except Exception:
        pass

    logger.info("DataFrame preprocessing completed successfully")
    logger.debug(
        f"Column mapping created: {len(column_mapping)} entries"
    )

    return processed_df

def get_original_column_name(df: pl.DataFrame, cleaned_name: str) -> str:
    if hasattr(df, "attrs"):
        attrs = getattr(df, "attrs", None)
        if attrs is not None and "column_mapping" in attrs:
            original_name = attrs["column_mapping"].get(cleaned_name, cleaned_name)
            if original_name != cleaned_name:
                logger.debug(
                    f"Retrieved original column name: '{cleaned_name}' -> '{original_name}'"
                )
            return original_name

    column_mapping = _df_column_mapping.get(id(df))
    if column_mapping is not None:
        original_name = column_mapping.get(cleaned_name, cleaned_name)
        if original_name != cleaned_name:
            logger.debug(
                f"Retrieved original column name: '{cleaned_name}' -> '{original_name}'"
            )
        return original_name

    logger.debug(f"No column mapping found, returning cleaned name: '{cleaned_name}'")
    return cleaned_name
