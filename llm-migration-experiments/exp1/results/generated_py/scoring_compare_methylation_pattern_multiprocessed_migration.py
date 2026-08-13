import logging
from multiprocessing import Pool

import polars as pl


def compare_methylation_pattern_multiprocessed(motifs_scored_in_bins, bin_consensus, choices, args, num_processes=1):
    logger = logging.getLogger(__name__)
    logger.info("Starting comparison of methylation patterns")
    
    motifs_scored_in_contigs = motifs_scored_in_bins.filter(pl.col("n_motifs") >= args.n_motif_contig_cutoff)
    motifs_scored_in_contigs = motifs_scored_in_contigs.select(["bin_contig", "motif_mod", "mean"]).rename({"bin_contig": "bin_compare"})

    comparison_score = pl.DataFrame()
    contigs_w_no_methylation = []

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(
            process_bin_contig,
            [
                (bin_contig, bin_consensus, motifs_scored_in_contigs, choices)
                for bin_contig in motifs_scored_in_contigs["bin_compare"].unique(maintain_order=True)
            ]
        )

    for result, no_methylation in results:
        if result is not None:
            comparison_score = pl.concat([comparison_score, result], how="vertical")
        if no_methylation is not None:
            contigs_w_no_methylation.append(no_methylation)

    return comparison_score, contigs_w_no_methylation
