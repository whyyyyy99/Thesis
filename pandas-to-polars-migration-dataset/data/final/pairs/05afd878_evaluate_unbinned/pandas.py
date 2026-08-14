import pandas as pd

    unbinned_otu_table = unbinned_otu_table.groupby(["gene", "sequence"]).first()[["target", "taxonomy"]].reset_index()
    unbinned_otu_table.dropna(inplace=True)
    unbinned_otu_table["target"] = unbinned_otu_table["target"].astype(str)
