def update_features(
    features: pd.DataFrame,
    values: dict | pd.DataFrame,
):
    for name, value in values.items():
        features[name] = value
    return features
