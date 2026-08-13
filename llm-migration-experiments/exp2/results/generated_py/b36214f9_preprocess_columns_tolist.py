import polars as pl

def clean_column_names(df: pl.DataFrame):
    original_columns = df.columns
    cleaned_columns = []

    for i, col in enumerate(original_columns):
        if col == "":
            cleaned_columns.append(f"column_{i}")
        else:
            cleaned_columns.append(str(col))

    return cleaned_columns, original_columns