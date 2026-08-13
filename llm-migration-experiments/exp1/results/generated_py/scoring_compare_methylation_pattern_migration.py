import numpy as np
import polars as pl

# Define conditions and compute comparison scores using numpy.select
conditions = [
    (motif_binary_compare["methylation_binary"] == 1) & (motif_binary_compare["methylation_binary_compare"] == 1),
    (motif_binary_compare["methylation_binary"] == 1) & (motif_binary_compare["methylation_binary_compare"] == 0),
    (motif_binary_compare["methylation_binary"] == 0) & (motif_binary_compare["methylation_binary_compare"] == 1),
    (motif_binary_compare["methylation_binary"] == 0) & (motif_binary_compare["methylation_binary_compare"] == 0),
    (motif_binary_compare["methylation_binary"] == 1) & (motif_binary_compare["methylation_binary_compare"].is_null()),
    (motif_binary_compare["methylation_binary"] == 0) & (motif_binary_compare["methylation_binary_compare"].is_null()),
]
motif_binary_compare = motif_binary_compare.with_columns(
    pl.select(
        conditions,
        choices,
        default=np.nan,
    ).alias("motif_comparison_score")
)
contig_bin_comparison_score = motif_binary_compare.group_by(["bin", "bin_compare"]).agg(
    pl.col("motif_comparison_score").sum().alias("binary_methylation_missmatch_score"),
    pl.col("motif_comparison_score").count().alias("non_na_comparisons"),
)
