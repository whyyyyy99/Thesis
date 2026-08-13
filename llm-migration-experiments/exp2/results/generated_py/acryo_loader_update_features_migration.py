import polars as pl


def update_features(
    features: pl.DataFrame,
    values: dict | pl.DataFrame,
):
    for name, value in values.items():
        if isinstance(value, pl.Series):
            features = features.with_columns(value.rename(name))
        elif isinstance(value, (str, bytes)) or not hasattr(value, "__len__"):
            features = features.with_columns(pl.lit(value).alias(name))
        else:
            features = features.with_columns(pl.Series(name, value))
    return features