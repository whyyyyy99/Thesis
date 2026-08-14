import pandas as pd

    binned_otu_table["sample"] = binned_otu_table["sample"].apply(lambda x: re.sub(r"\.1$", "", x))
    nontarget_otu_table = (binned_otu_table
        .set_index(["sample"])[["gene", "sequence", "taxonomy", "found_in"]]
        .join(elusive_clusters)
        .dropna(subset=["coassembly"])
        .drop_duplicates()
        .set_index(["coassembly", "gene", "sequence"])
        )
    nontarget_otu_table["target"] = None

    haystack_otu_table = pd.concat([elusive_otu_table, nontarget_otu_table])
