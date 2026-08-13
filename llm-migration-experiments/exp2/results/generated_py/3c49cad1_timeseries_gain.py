import polars as pl

def gain_of_value_pairs(old_values: pl.DataFrame, new_values: pl.Series) -> float:
    old_score = old_values.select((pl.sum_horizontal(pl.all().is_not_null()) >= 4).sum()).item()
    old_values[f"S{new_values.name}"] = new_values
    new_score = old_values.select((pl.sum_horizontal(pl.all().is_not_null()) >= 4).sum()).item()