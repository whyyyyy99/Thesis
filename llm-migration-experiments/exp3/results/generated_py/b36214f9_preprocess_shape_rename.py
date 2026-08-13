import polars as pl


def preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    processed_df = df.clone()
    processed_df.columns = cleaned_columns

    return processed_df
