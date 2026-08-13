import math
import polars as pl

def get_rmse(regular_values: pl.Series, interpolated_values: pl.Series):
    diff = (regular_values - interpolated_values).drop_nulls().drop_nans()
    n = diff.len()
    if n == 0:
        return float("nan")
    return ((diff**2).sum() / n) ** 0.5
