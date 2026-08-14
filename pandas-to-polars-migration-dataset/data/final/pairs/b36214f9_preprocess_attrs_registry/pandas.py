import pandas as pd

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    processed_df = df.copy()
    processed_df.columns = cleaned_columns

    processed_df.attrs["original_columns"] = original_columns
    processed_df.attrs["column_mapping"] = dict(zip(cleaned_columns, original_columns))

    logger.info("DataFrame preprocessing completed successfully")
    logger.debug(
        f"Column mapping created: {len(processed_df.attrs['column_mapping'])} entries"
    )

    return processed_df

def get_original_column_name(df: pd.DataFrame, cleaned_name: str) -> str:
    if hasattr(df, "attrs") and "column_mapping" in df.attrs:
        original_name = df.attrs["column_mapping"].get(cleaned_name, cleaned_name)
        if original_name != cleaned_name:
            logger.debug(
                f"Retrieved original column name: '{cleaned_name}' -> '{original_name}'"
            )
        return original_name

    logger.debug(f"No column mapping found, returning cleaned name: '{cleaned_name}'")
    return cleaned_name
