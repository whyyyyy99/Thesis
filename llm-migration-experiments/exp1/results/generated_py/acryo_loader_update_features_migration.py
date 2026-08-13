import polars as pl


def update_features(
    features: pl.DataFrame,
    values: dict | pl.DataFrame,
):
    if isinstance(values, pl.DataFrame):
        items = ((name, values.get_column(name)) for name in values.columns)
    else:
        items = values.items()

    for name, value in items:
        features = features.with_columns(pl.lit(value).alias(name)) if not isinstance(value, (pl.Series, list, tuple)) else features.with_columns(pl.Series(name, value))
        if isinstance(value, pl.Series):
            features = features.with_columns(value.alias(name))
    return features
