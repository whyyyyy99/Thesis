import pandas as pd

def gain_of_value_pairs(old_values: pd.DataFrame, new_values: pd.Series) -> float:
    old_score = old_values.apply(lambda row: row.dropna().size >= 4).sum()  # 5: dates plus 4 values
    old_values.loc[:, f"S{new_values.name}"] = new_values.values  # Add new column
    new_score = old_values.apply(lambda row: row.dropna().size >= 4).sum()  # 5: dates plus 4 values
