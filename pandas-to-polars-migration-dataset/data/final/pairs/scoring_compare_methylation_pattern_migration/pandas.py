import pandas as pd

# Define conditions and compute comparison scores using numpy.select
conditions = [
    (motif_binary_compare["methylation_binary"] == 1) & (motif_binary_compare["methylation_binary_compare"] == 1),
    (motif_binary_compare["methylation_binary"] == 1) & (motif_binary_compare["methylation_binary_compare"] == 0),
    (motif_binary_compare["methylation_binary"] == 0) & (motif_binary_compare["methylation_binary_compare"] == 1),
    (motif_binary_compare["methylation_binary"] == 0) & (motif_binary_compare["methylation_binary_compare"] == 0),
    (motif_binary_compare["methylation_binary"] == 1) & (motif_binary_compare["methylation_binary_compare"].isna()),
    (motif_binary_compare["methylation_binary"] == 0) & (motif_binary_compare["methylation_binary_compare"].isna()),
]
motif_binary_compare["motif_comparison_score"] = np.select(conditions, choices, default=np.nan)
contig_bin_comparison_score = motif_binary_compare.groupby(["bin", "bin_compare"]).agg(
    binary_methylation_missmatch_score=pd.NamedAgg(column="motif_comparison_score", aggfunc="sum"),
    non_na_comparisons=pd.NamedAgg(column="motif_comparison_score", aggfunc="count")
).reset_index()
