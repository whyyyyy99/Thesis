import pandas as pd

        checkm_out = pd.read_csv(checkm_out_dict[coassembly], sep = "\t")
        passed_bins = checkm_out[(checkm_out[completeness_col] >= min_completeness) & (checkm_out[contamination_col] <= max_contamination)]["Bin Id"].to_list()
