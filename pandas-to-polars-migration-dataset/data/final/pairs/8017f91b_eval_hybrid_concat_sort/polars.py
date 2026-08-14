    average_precision_scores = pl.concat(
        [...]
    ).with_columns(pl.max(pl.exclude(["Query Document ID", "Language Model"])).alias("Best Score"))
    average_precision_scores.sort(by="Best Score", descending=True).unique(
        subset="Query Document ID"
    )
