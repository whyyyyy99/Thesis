import polars as pl

treated_array = treated_set.select(covariates).to_numpy().astype(float)
control_array = control_set.select(covariates).to_numpy().astype(float)

treated_prop, control_prop = calculate_propensity(
    x_train,
    y_train,
    treated_array,
    control_array,
    hyperparam=hyperparam,
    metric=model,
)

# Add propensity score to the original data
treated_set = treated_set.with_columns(pl.Series("Prop. score", treated_prop))
control_set = control_set.with_columns(pl.Series("Prop. score", control_prop))

matched_control = nearest_neighbor(
    treated_set, control_set, metric="absolute", covariates=["Prop. score"]
)

matched_control = matched_control.drop("Prop. score")
treated_set = treated_set.drop("Prop. score")
control_set = control_set.drop("Prop. score")