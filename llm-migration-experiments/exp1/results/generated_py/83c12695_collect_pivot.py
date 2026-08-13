import polars as pl

appraise_binned = appraise_binned.with_columns(
    pl.col("found_in").str.split(",")
).explode("found_in").with_columns(
    pl.col("found_in").str.replace("_protein$", "", literal=False)
)

trimmed_binned = (
    appraise_binned.group_by(["gene", "found_in"])
    .agg(pl.col("coverage").sum())
    .pivot(index="gene", on="found_in", values="coverage")
    .unpivot(index="gene", variable_name="found_in", value_name="value")
    .fill_null(0)
    .group_by("found_in")
    .agg(pl.col("value"))
    .with_columns(pl.col("value").map_elements(trimmed_mean))
)

reference_bins = set(
    trimmed_binned.filter(pl.col("value") > 0)["found_in"].to_list()
)
