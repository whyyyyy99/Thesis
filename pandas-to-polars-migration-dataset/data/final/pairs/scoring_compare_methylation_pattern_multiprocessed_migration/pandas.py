import pandas as pd

def compare_methylation_pattern_multiprocessed(motifs_scored_in_bins, bin_consensus, choices, args, num_processes=1):
    logger = logging.getLogger(__name__)
    logger.info("Starting comparison of methylation patterns")
    
    motifs_scored_in_contigs = motifs_scored_in_bins[motifs_scored_in_bins["n_motifs"] >= args.n_motif_contig_cutoff]
    motifs_scored_in_contigs = motifs_scored_in_contigs[["bin_contig", "motif_mod", "mean"]]
    motifs_scored_in_contigs.rename(columns={"bin_contig": "bin_compare"}, inplace=True)

    comparison_score = pd.DataFrame()
    contigs_w_no_methylation = []

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(
            process_bin_contig,
            [
                (bin_contig, bin_consensus, motifs_scored_in_contigs, choices)
                for bin_contig in motifs_scored_in_contigs["bin_compare"].unique()
            ]
        )

    for result, no_methylation in results:
        if result is not None:
            comparison_score = pd.concat([comparison_score, result])
        if no_methylation is not None:
            contigs_w_no_methylation.append(no_methylation)

    return comparison_score, contigs_w_no_methylation
