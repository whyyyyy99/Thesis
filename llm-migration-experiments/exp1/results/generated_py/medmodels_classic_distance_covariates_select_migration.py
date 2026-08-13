import polars as pl

columns = treated_set.columns

if not covariates:
    covariates = columns

treated_array = treated_set.select(covariates).to_numpy().astype(float)
control_array = control_set.select(covariates).to_numpy().astype(float)
