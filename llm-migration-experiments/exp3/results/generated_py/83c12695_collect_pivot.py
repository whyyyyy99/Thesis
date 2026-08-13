import polars as pl

appraise_binned = appraise_binned.with_columns(
    pl.col("found_in").str.split(",")
).explode("found_in").with_columns(
    pl.col("found_in").str.replace(r"_protein$", "")
)

trimmed_binned = (
    appraise_binned.group_by(["gene", "found_in"])
    .agg(pl.col("coverage").sum().alias("coverage"))
    .pivot(index="gene", on="found_in", values="coverage")
    .unpivot(index="gene")
    .fill_null(0)
    .group_by("variable")
    .map_groups(
        lambda df: pl.DataFrame(
            {
                "found_in": [df["variable"][0]],
                "value": [trimmed_mean(df["value"])],
            }
        )
    )
    .rename({"variable": "found_in"})
)

reference_bins = set(
    trimmed_binned.filter(pl.col("value") > 0)["found_in"].to_list()
)
