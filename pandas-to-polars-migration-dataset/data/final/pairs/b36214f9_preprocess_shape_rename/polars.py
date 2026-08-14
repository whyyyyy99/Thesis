import polars as pl

def preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.height} rows, {df.width} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    column_mapping = dict(zip(original_columns, cleaned_columns))
    processed_df = df.rename(column_mapping)

    return processed_df
