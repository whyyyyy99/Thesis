def gain_of_value_pairs(old_values: pl.DataFrame, new_values: pl.Series) -> float:
    old_score = (
        old_values.select(pl.fold(acc=0, function=lambda acc, s: acc + s.is_not_null(), exprs=pl.all()) >= 4)
        .sum()
        .item()
    )  # 5: dates plus 4 values
    old_values = old_values.with_columns(pl.lit(new_values).alias(f"S{new_values.name}"))
    new_score = (
        old_values.select(pl.fold(acc=0, function=lambda acc, s: acc + s.is_not_null(), exprs=pl.all()) >= 4)
        .sum()
        .item()
    )  # 5: dates plus 4 values
