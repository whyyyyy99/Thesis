import pandas as pd

def get_rmse(regular_values: pd.Series, interpolated_values: pd.Series):
    diff = (regular_values.reset_index(drop=True) - interpolated_values.reset_index(drop=True)).dropna()
    n = diff.size
    return ((diff**2).sum() / n) ** 0.5
