    unbinned = unbinned.drop("found_in"
    ).with_row_count("target"
    ).select(
        "gene", "sample", "sequence", "num_hits", "coverage", "taxonomy",
        pl.first("target").over(["gene", "sequence"]).rank("dense") - 1,
    ).with_columns(
        pl.col("target").cast(pl.Utf8)
    )
