import numpy as np
import polars as pl
from typing import List, Optional, Union

def nearest_neighbor(
    treated_set: pl.DataFrame,
    control_set: pl.DataFrame,
    metric: str,
    covariates: Optional[Union[List[str], pl.Series]] = None,
) -> pl.DataFrame:
    columns = treated_set.columns

    if not covariates:
        covariates = columns

    treated_array = treated_set.select(covariates).to_numpy().astype(float)
    control_array = control_set.select(covariates).to_numpy().astype(float)
    control_array_full = control_set.to_numpy()
    matched_rows = []

    cov = np.array([])
    if metric == "mahalanobis":
        cov = np.cov(np.concatenate((treated_array, control_array)).T)

    for element_ss in treated_array:
        if metric == "mahalanobis":
            if cov.ndim == 0:
                inv_cov = 1 / cov
            else:
                try:
                    inv_cov = np.linalg.inv(cov)
                except np.linalg.LinAlgError:
                    raise ValueError(
                        "The covariance matrix is singular. Please, check the data."
                    )

            dist = [
                metrics.mahalanobis_metric(element_ss, element_bs, inv_cov=inv_cov)
                for element_bs in control_array
            ]

        else:
            metric_function = metrics.METRICS[metric]

            dist = [
                metric_function(element_ss, element_bs) for element_bs in control_array
            ]

        nn_index = np.argmin(dist)

        new_row = {col: float(val) for col, val in zip(columns, control_array_full[nn_index])}
        matched_rows.append(new_row)

        control_array_full = np.delete(control_array_full, nn_index, 0)
        control_array = np.delete(control_array, nn_index, 0)

    matched_group = pl.DataFrame(matched_rows, schema={col: pl.Float64 for col in columns}) if matched_rows else pl.DataFrame(schema={col: pl.Float64 for col in columns})

    return matched_group
