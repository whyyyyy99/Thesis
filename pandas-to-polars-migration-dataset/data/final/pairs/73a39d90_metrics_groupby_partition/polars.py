import polars as pl

def summarize_metrics(df: pl.DataFrame, metrics: list[str]) -> pl.DataFrame:
    """Compute descriptive statistics for each metric by condition."""
    grouped = df.partition_by("condition", as_dict=True)
    stats: list[dict[str, float | str]] = []
    for condition_key in sorted(grouped.keys()):
        if isinstance(condition_key, tuple):
            condition = condition_key[0]
        else:
            condition = condition_key
        group = grouped[condition_key]
        for metric in metrics:
            values = group.get_column(metric).to_numpy()
            stats.append(
                {
                    "condition": condition,
                    "metric": metric,
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values, ddof=1)),
                    "q10": float(np.quantile(values, 0.1, method="linear")),
                    "q90": float(np.quantile(values, 0.9, method="linear")),
                }
            )
    return pl.DataFrame(stats)
