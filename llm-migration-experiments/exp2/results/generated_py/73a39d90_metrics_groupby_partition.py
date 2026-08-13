import polars as pl

def summarize_metrics(df: pl.DataFrame, metrics: list[str]) -> pl.DataFrame:
    """Compute descriptive statistics for each metric by condition."""
    stats = []
    conditions = df.select("condition").drop_nulls().unique().sort("condition")["condition"].to_list()
    for cond in conditions:
        group = df.filter(pl.col("condition") == cond)
        for metric in metrics:
            series = group[metric]
            stats.append(
                {
                    "condition": cond,
                    "metric": metric,
                    "mean": series.mean(),
                    "median": series.median(),
                    "std": series.std(),
                    "q10": series.quantile(0.1, interpolation="linear"),
                    "q90": series.quantile(0.9, interpolation="linear"),
                }
            )
    return pl.DataFrame(stats)