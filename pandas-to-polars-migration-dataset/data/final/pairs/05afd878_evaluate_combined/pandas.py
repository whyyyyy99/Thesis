import pandas as pd

    combined_otu_table = recovered_otu_table.set_index(["coassembly", "gene", "sequence"])[["genome", "taxonomy"]].join(haystack_otu_table, how="outer", rsuffix="old").reset_index()
    combined_otu_table["taxonomy"] = combined_otu_table["taxonomy"].combine(combined_otu_table["taxonomyold"], lambda a,b: a if not pd.isna(a) else b)
    combined_otu_table = combined_otu_table.drop("taxonomyold", axis=1)
    combined_otu_table = combined_otu_table[combined_otu_table["coassembly"].isin(recovered_coassemblies)]
    combined_otu_table = combined_otu_table[combined_otu_table["genome"].notnull() | combined_otu_table["target"].notnull()]
