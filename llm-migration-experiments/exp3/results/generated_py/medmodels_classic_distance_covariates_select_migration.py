columns = treated_set.columns

if not covariates:
    covariates = columns

treated_array = treated_set.select(covariates).cast(float).to_numpy()
control_array = control_set.select(covariates).cast(float).to_numpy()
