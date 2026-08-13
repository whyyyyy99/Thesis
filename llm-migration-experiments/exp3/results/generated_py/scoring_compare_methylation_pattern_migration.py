import numpy as np
import polars as pl

motif_binary_compare = motif_binary_compare.with_columns(
    pl.when((pl.col("methylation_binary") == 1) & (pl.col("methylation_binary_compare") == 1))
    .then(choices[0])
    .when((pl.col("methylation_binary") == 1) & (pl.col("methylation_binary_compare") == 0))
    .then(choices[1])
    .when((pl.col("methylation_binary") == 0) & (pl.col("methylation_binary_compare") == 1))
    .then(choices[2])
    .when((pl.col("methylation_binary") == 0) & (pl.col("methylation_binary_compare") == 0))
    .then(choices[3])
    .when((pl.col("methylation_binary") == 1) & (pl.col("methylation_binary_compare").is_null()))
    .then(choices[4])
    .when((pl.col("methylation_binary") == 0) & (pl.col("methylation_binary_compare").is_null()))
    .then(choices[5])
    .otherwise(pl.lit(None, dtype=pl.Float64))
    .alias("motif_comparison_score")
)

contig_bin_comparison_score = (
    motif_binary_compare.group_by(["bin", "bin_compare"])
    .agg(
        pl.col("motif_comparison_score").sum().alias("binary_methylation_missmatch_score"),
        pl.col("motif_comparison_score").count().alias("non_na_comparisons"),
    )
    .sort(["bin", "bin_compare"])
)
