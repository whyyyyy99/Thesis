def update_features(
    features: pl.DataFrame,
    values: dict[str, Any] | pl.DataFrame | list[Any],
):
    """Update features with new values."""
    if isinstance(values, dict):
        _values = [pl.Series(k, v) for k, v in values.items()]
    else:
        _values = list(values)
    return features.with_columns(_values)
