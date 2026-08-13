import polars as pl


def summarize_metrics(df: pl.DataFrame, metrics: list[str]) -> pl.DataFrame:
    """Compute descriptive statistics for each metric by condition."""
    stats = []
    if "condition" not in df.columns:
        return pl.DataFrame(stats)

    conditions = df.get_column("condition").drop_nulls().unique().sort()

    for cond in conditions:
        group = df.filter(pl.col("condition") == cond)
        for metric in metrics:
            series = group.get_column(metric)
            stats.append(
                {
                    "condition": cond,
                    "metric": metric,
                    "mean": series.mean(),
                    "median": series.median(),
                    "std": series.std(),
                    "q10": series.quantile(0.1),
                    "q90": series.quantile(0.9),
                }
            )
    return pl.DataFrame(stats)
