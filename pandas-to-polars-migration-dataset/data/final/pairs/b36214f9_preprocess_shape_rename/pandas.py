import pandas as pd

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(
        f"Starting DataFrame preprocessing: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    cleaned_columns, original_columns = clean_column_names(df)

    processed_df = df.copy()
    processed_df.columns = cleaned_columns

    processed_df.attrs["original_columns"] = original_columns

    return processed_df
