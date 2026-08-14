import polars as pl

def nearest_neighbor(
    treated_set: pl.DataFrame,
    control_set: pl.DataFrame,
    metric: metrics.Metric,
    number_of_neighbors: int = 1,
    covariates: Optional[MedRecordAttributeInputList] = None,
) -> pl.DataFrame:
    if not covariates:
        covariates = treated_set.columns

    treated_array = treated_set.select(covariates).to_numpy().astype(float)
    control_array = control_set.select(covariates).to_numpy().astype(float)
    control_array_full = control_set.to_numpy()
    matched_control = []

    cov = np.array([])
    if metric == "mahalanobis":
        cov = np.cov(np.concatenate((treated_array, control_array)).T)

    for treated_subject in treated_array:
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
                metrics.mahalanobis_metric(
                    treated_subject, control_subject, inv_cov=inv_cov
                )
                for control_subject in control_array
            ]

        else:
            metric_function = metrics.METRICS[metric]

            dist = [
                metric_function(treated_subject, control_subject)
                for control_subject in control_array
            ]

        neighbor_indices = np.argpartition(dist, number_of_neighbors)[
            :number_of_neighbors
        ]

        for neighbor_index in neighbor_indices:
            new_row = pl.DataFrame(
                [control_array_full[neighbor_index]], schema=treated_set.columns
            )
            matched_control.append(new_row)

            control_array_full = np.delete(control_array_full, neighbor_index, 0)
            control_array = np.delete(control_array, neighbor_index, 0)

    return pl.concat(matched_control, how="vertical")
