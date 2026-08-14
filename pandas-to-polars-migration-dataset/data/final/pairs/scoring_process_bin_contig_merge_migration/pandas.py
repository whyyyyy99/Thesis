import pandas as pd

worker_setup_logging(log_queue)
motif_binary_compare = pd.merge(
    bin_motifs_from_motifs_scored_in_bins,
    motifs_scored_in_contigs[motifs_scored_in_contigs["bin_compare"] == bin_contig],
    on="motif_mod"
)
contigHasNMethylation = motif_binary_compare["methylation_binary_compare"].sum()
