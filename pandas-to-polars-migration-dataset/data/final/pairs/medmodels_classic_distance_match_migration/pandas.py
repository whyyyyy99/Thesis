import pandas as pd

def nearest_neighbor(
    treated_set: pd.DataFrame,
    control_set: pd.DataFrame,
    metric: str,
    covariates: Optional[Union[List[str], pd.Index[str]]] = None,
) -> pd.DataFrame:
    columns = treated_set.columns

    if not covariates:
        covariates = columns

    treated_array = treated_set[covariates].to_numpy().astype(float)
    control_array = control_set[covariates].to_numpy().astype(float)
    control_array_full = control_set.to_numpy()
    matched_group = pd.DataFrame(columns=columns)

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

        new_row = pd.DataFrame(control_array_full[nn_index], index=columns)
        matched_group = (
            new_row.transpose().astype(float).copy()
            if matched_group.empty
            else pd.concat([matched_group, new_row.transpose().astype(float)])
        )
        control_array_full = np.delete(control_array_full, nn_index, 0)
        control_array = np.delete(control_array, nn_index, 0)

    return matched_group.reset_index(drop=True)
