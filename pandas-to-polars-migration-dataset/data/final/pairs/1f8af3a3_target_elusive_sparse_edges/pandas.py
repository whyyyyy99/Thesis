import pandas as pd

    sparse_edges = (sample_pairs
        .groupby(["taxa_group", "sample_pairs"])["target"]
        .agg(["count", lambda x: ",".join(sorted(x))])
        .reset_index()
        )
    sparse_edges.rename(columns = {"count": "weight", "<lambda_0>": "target_ids"}, inplace=True)
