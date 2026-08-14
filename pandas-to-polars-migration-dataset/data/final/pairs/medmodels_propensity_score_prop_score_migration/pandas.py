import pandas as pd

treated_array = treated_set[covariates].to_numpy().astype(float)
control_array = control_set[covariates].to_numpy().astype(float)

treated_prop, control_prop = calculate_propensity(
        x_train,
        y_train,
        treated_array,
        control_array,
        hyperparam=hyperparam,
        metric=model,
    )

# Add propensity score to the original data
treated_set["Prop. score"] = treated_prop
control_set["Prop. score"] = control_prop

matched_control = nearest_neighbor(
    treated_set, control_set, metric="absolute", covariates=["Prop. score"]
)

matched_control.pop("Prop. score")
treated_set.pop("Prop. score")
control_set.pop("Prop. score")
