    binned = appraised.filter(pl.col("binned")).drop(["divergence", "binned"])
    unbinned = pipe_read.join(
        appraised, on=["gene", "sample", "sequence", "num_hits", "coverage", "taxonomy"], how="left"
    ).filter(~pl.col("binned").fill_null(False)
    ).drop(["divergence", "binned"]
    ).with_columns(
        pl.lit(None).cast(str).alias("found_in")
    )
