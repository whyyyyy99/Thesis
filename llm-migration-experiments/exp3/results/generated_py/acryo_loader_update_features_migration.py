import polars as pl
from collections.abc import Mapping


def update_features(
    features: pl.DataFrame,
    values: dict | pl.DataFrame,
):
    for name, value in values.items():
        if isinstance(value, pl.Series):
            features = features.with_columns(value.rename(name))
        elif isinstance(value, Mapping):
            features = features.with_columns(pl.Series(name, value))
        else:
            try:
                features = features.with_columns(pl.Series(name, value))
            except Exception:
                features = features.with_columns(pl.lit(value).alias(name))
    return features
