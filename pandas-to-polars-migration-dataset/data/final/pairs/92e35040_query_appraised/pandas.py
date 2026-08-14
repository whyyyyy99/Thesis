import pandas as pd

    appraised = (query_read
        .rename(columns = {"marker": "gene", "query_name":"sample", "query_sequence": "sequence", "sample": "found_in"})
        .drop(["taxonomy", "num_hits", "coverage"], axis=1, errors="ignore")
        .set_index(["gene", "sample", "sequence"])
        .join(pipe_read.set_index(["gene", "sample", "sequence"]), on = ["gene", "sample", "sequence"], how = "inner")
        .reset_index()
        .groupby(["gene", "sample", "sequence", "num_hits", "coverage", "taxonomy", "divergence"])["found_in"]
        .agg(lambda x: ",".join(sorted(x)))
        .reset_index()
        )
