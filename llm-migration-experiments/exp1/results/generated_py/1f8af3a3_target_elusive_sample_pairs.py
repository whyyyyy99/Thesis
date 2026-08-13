import polars as pl

sample_pairs = (
    unbinned.group_by("target", maintain_order=True)
    .map_groups(
        lambda group_df: pl.DataFrame(
            {
                "target": [group_df["target"][0]],
                "sample_pairs": [find_pairs(group_df)],
            }
        )
    )
    .explode("sample_pairs")
    .drop_nulls(subset=["sample_pairs"])
    .join(taxonomy, on="target", how="left")
)
sample_pairs = sample_pairs.with_columns(
    pl.col("taxonomy").map_elements(get_taxa_group).alias("taxa_group")
)
sample_pairs = sample_pairs.drop_nulls(subset=["taxa_group"])
