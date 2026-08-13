import polars as pl

appraise_binned = appraise_binned.with_columns(
    pl.col("found_in").str.split(",")
).explode("found_in").with_columns(
    pl.col("found_in").str.replace_all(r"_protein$", "")
)

trimmed_binned = (
    appraise_binned.group_by(["gene", "found_in"])
    .agg(pl.col("coverage").sum())
    .pivot(index="gene", on="found_in", values="coverage")
    .melt(id_vars="gene")
    .fill_null(0)
    .group_by("variable")
    .agg(pl.col("value").map_groups(lambda ss: trimmed_mean(ss[0]), return_dtype=pl.Float64).alias("value"))
    .rename({"variable": "found_in"})
)

reference_bins = set(
    trimmed_binned.filter(pl.col("value") > 0).get_column("found_in").to_list()
)