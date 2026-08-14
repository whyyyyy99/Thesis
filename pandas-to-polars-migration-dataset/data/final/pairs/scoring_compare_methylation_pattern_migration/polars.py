# Compute comparison scores using Polars expressions and group by with Polars
motif_comparison_score = (
    pl.when((motif_binary_compare['methylation_binary'] == 1) & (motif_binary_compare['methylation_binary_compare'] == 1))
    .then(0)
    .when((motif_binary_compare['methylation_binary'] == 1) & (motif_binary_compare['methylation_binary_compare'] == 0))
    .then(1)
    .when((motif_binary_compare['methylation_binary'] == 0) & (motif_binary_compare['methylation_binary_compare'] == 1))
    .then(1)
    .when((motif_binary_compare['methylation_binary'] == 0) & (motif_binary_compare['methylation_binary_compare'] == 0))
    .then(0)
    .when((motif_binary_compare['methylation_binary'] == 1) & (motif_binary_compare['methylation_binary_compare'].is_null()))
    .then(0)
    .when((motif_binary_compare['methylation_binary'] == 0) & (motif_binary_compare['methylation_binary_compare'].is_null()))
    .then(0)
    .otherwise(pl.lit(None))
)
motif_binary_compare = motif_binary_compare.with_columns(motif_comparison_score.alias("motif_comparison_score"))
contig_bin_comparison_score = motif_binary_compare.group_by(["bin", "bin_compare"]).agg([
    pl.sum("motif_comparison_score").alias("binary_methylation_missmatch_score"),
    pl.count("motif_comparison_score").alias("non_na_comparisons")
])
