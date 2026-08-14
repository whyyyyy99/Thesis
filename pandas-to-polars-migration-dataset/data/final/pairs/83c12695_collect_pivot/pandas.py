import pandas as pd

    appraise_binned["found_in"] = appraise_binned["found_in"].str.split(",")
    appraise_binned = appraise_binned.explode("found_in")
    appraise_binned["found_in"] = appraise_binned["found_in"].str.replace("_protein$", "", regex=True)

    trimmed_binned = (appraise_binned.groupby(["gene", "found_in"])["coverage"]
        .sum()
        .reset_index()
        .pivot(index="gene", columns="found_in", values="coverage")
        .reset_index()
        .melt(id_vars="gene")
        .fillna(0)
        .groupby("found_in")["value"]
        .apply(trimmed_mean)
        .reset_index()
        )
    reference_bins = set(trimmed_binned[trimmed_binned["value"] > 0]["found_in"].to_list())
