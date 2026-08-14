    appraised = query_read.rename(
        {"marker": "gene", "query_name":"sample", "query_sequence": "sequence", "sample": "found_in"}
    ).drop([
        "taxonomy", "num_hits", "coverage"
    ]).join(
        pipe_read, on=["gene", "sample", "sequence"], how="inner"
    ).groupby(
        ["gene", "sample", "sequence", "num_hits", "coverage", "taxonomy", "divergence"]
    ).agg(
        pl.col("found_in").sort().str.concat(",")
    ).with_columns(
        pl.col("divergence").alias("binned") <= ((1 - SEQUENCE_IDENTITY) * WINDOW_SIZE)
    )
