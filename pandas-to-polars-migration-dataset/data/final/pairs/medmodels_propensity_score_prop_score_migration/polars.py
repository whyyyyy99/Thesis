treated_array = treated_set.select(covariates).to_numpy().astype(float)
control_array = control_set.select(covariates).to_numpy().astype(float)

treated_prop, control_prop = calculate_propensity(
        x_train,
        y_train,
        treated_array,
        control_array,
        hyperparam=hyperparam,
        model=model,
    )

# Add propensity score to the original data
treated_set = treated_set.with_columns(pl.Series("prop_score", treated_prop))
control_set = control_set.with_columns(pl.Series("prop_score", control_prop))

matched_control = nearest_neighbor(
        treated_set,
        control_set,
        metric=metric,
        number_of_neighbors=number_of_neighbors,
        covariates=["prop_score"],
    )

matched_control = matched_control.drop("prop_score")
treated_set = treated_set.drop("prop_score")
control_set = control_set.drop("prop_score")
