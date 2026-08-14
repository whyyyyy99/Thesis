def get_rmse(regular_values: pl.Series, interpolated_values: pl.Series):
    n = regular_values.len()
    return (((regular_values - interpolated_values).drop_nulls() ** 2).sum() / n) ** 0.5
