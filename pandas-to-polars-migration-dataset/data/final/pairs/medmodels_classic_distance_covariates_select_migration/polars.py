if not covariates:
    covariates = treated_set.columns

treated_array = treated_set.select(covariates).to_numpy().astype(float)
control_array = control_set.select(covariates).to_numpy().astype(float)
