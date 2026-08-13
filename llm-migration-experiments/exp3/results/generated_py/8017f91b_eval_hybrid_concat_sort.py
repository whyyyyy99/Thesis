import polars as pl

average_precision_scores = pl.concat(frames)
return (
    average_precision_scores
    .sort("Best Score", descending=True)
    .unique(subset="Query Document ID", keep="first", maintain_order=True)
)
