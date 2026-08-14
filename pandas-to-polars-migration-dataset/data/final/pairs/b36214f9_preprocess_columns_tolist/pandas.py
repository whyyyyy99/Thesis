import pandas as pd

def clean_column_names(df: pd.DataFrame):
    original_columns = df.columns.tolist()
    cleaned_columns = []

    for i, col in enumerate(original_columns):
        if pd.isna(col) or col == "":
            cleaned_columns.append(f"column_{i}")
        else:
            cleaned_columns.append(str(col))

    return cleaned_columns, original_columns
