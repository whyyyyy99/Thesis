worker_setup_logging(log_queue)
motif_binary_compare = bin_motifs_from_motifs_scored_in_bins.join(
    motifs_scored_in_contigs.filter(pl.col("bin_compare") == bin_contig),
    on="motif_mod",
    how="inner",
)
contigHasNMethylation = motif_binary_compare.select(
    pl.col("methylation_binary_compare").sum()
).item()