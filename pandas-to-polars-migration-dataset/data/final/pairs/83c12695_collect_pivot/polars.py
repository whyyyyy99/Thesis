    reference_bins = appraise_binned.with_columns(
        pl.col("found_in").str.split(",")
    ).explode(
        "found_in"
    ).with_columns(
        pl.col("found_in").str.replace("_protein$", "")
    ).groupby(
        ["gene", "found_in"]
    ).agg(
        pl.col("coverage").sum()
    ).pivot(
        values="coverage", index="gene", columns="found_in",
    ).melt(
        id_vars="gene", variable_name="found_in", value_name="coverage"
    ).fill_null(0
    ).groupby(
        "found_in"
    ).agg(
        (pl.col("coverage").len() * TRIM_FRACTION).floor().cast(int).alias("cut"),
        pl.col("coverage")
    ).with_columns(
        pl.col("coverage").arr.sort().arr.slice(
            pl.col("cut"), pl.col("coverage").arr.lengths() - 2 * pl.col("cut")
        ).arr.mean()
    ).filter(
        pl.col("coverage") > 0
    ).get_column("found_in"
    ).to_list()
    return set(reference_bins)
