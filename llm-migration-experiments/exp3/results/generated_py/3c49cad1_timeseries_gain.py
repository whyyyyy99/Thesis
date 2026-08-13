import polars as pl

def gain_of_value_pairs(old_values: pl.DataFrame, new_values: pl.Series) -> float:
    old_score = old_values.select(
        pl.sum_horizontal(pl.all().is_not_null().cast(pl.Int64)) >= 4
    ).to_series().sum()  # 5: dates plus 4 values
    old_values = old_values.with_columns(
        pl.Series(f"S{new_values.name}", new_values.to_list())
    )  # Add new column
    new_score = old_values.select(
        pl.sum_horizontal(pl.all().is_not_null().cast(pl.Int64)) >= 4
    ).to_series().sum()  # 5: dates plus 4 values
