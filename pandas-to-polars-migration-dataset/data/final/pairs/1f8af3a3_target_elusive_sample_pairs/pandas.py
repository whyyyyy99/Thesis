import pandas as pd

    sample_pairs = (unbinned
        .groupby("target")
        .apply(find_pairs)
        .to_frame("sample_pairs")
        .explode("sample_pairs")
        .dropna(subset = "sample_pairs")
        .join(taxonomy)
        .reset_index()
        )
    sample_pairs["taxa_group"] = sample_pairs["taxonomy"].apply(get_taxa_group)
    sample_pairs = sample_pairs.dropna(subset = "taxa_group")
