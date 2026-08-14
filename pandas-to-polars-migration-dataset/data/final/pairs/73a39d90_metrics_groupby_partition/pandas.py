import pandas as pd

def summarize_metrics(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Compute descriptive statistics for each metric by condition."""
    stats = []
    for cond, group in df.groupby("condition"):
        for metric in metrics:
            series = group[metric]
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
    return pd.DataFrame(stats)
