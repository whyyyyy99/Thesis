        checkm_out = pl.read_csv(checkm_out_dict[coassembly], sep = "\t")
        passed_bins = checkm_out.filter(
            (pl.col(completeness_col) >= min_completeness) & (pl.col(contamination_col) <= max_contamination),
        ).get_column("Bin Id"
        ).to_list()
