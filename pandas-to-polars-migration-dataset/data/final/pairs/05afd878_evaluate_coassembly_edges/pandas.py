import pandas as pd

    elusive_edges["sample1"] = elusive_edges["sample1"].apply(lambda x: re.sub(r"\.1$", "", x))
    elusive_edges["sample2"] = elusive_edges["sample2"].apply(lambda x: re.sub(r"\.1$", "", x))
    elusive_edges = (elusive_edges
        .set_index("sample1")
        .join(elusive_clusters)
        .reset_index()
        .rename(columns={"index": "sample1"})
        .set_index("sample2")
        .join(elusive_clusters, rsuffix="2")
        .reset_index()
        .rename(columns={"index": "sample2"})
        )
    coassembly_edges = elusive_edges[elusive_edges["coassembly"] == elusive_edges["coassembly2"]].copy()
    coassembly_edges["target"] = coassembly_edges["target_ids"].str.split(",")
    coassembly_edges = coassembly_edges.explode("target").drop_duplicates(["target", "coassembly"]).set_index("target")[["coassembly"]]
