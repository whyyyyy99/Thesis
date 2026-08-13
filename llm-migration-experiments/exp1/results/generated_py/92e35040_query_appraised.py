import polars as pl

appraised = (
    query_read
    .rename({"marker": "gene", "query_name": "sample", "query_sequence": "sequence", "sample": "found_in"})
    .drop(["taxonomy", "num_hits", "coverage"], strict=False)
    .join(pipe_read, on=["gene", "sample", "sequence"], how="inner")
    .group_by(["gene", "sample", "sequence", "num_hits", "coverage", "taxonomy", "divergence"])
    .agg(pl.col("found_in").sort().implode().list.join(","))
)
