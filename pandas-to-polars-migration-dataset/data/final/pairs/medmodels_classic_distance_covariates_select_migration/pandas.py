import pandas as pd

columns = treated_set.columns

if not covariates:
    covariates = columns

treated_array = treated_set[covariates].to_numpy().astype(float)
control_array = control_set[covariates].to_numpy().astype(float)
