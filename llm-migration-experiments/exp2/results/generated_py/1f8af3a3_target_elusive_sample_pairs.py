import polars as pl

_sample_pairs_rows = []
for target, data in unbinned.group_by("target", maintain_order=True):
    res = find_pairs(data)
    if isinstance(res, pl.DataFrame):
        values = res.to_series(0).to_list() if res.width == 1 else res.rows()
    elif isinstance(res, pl.Series):
        values = res.to_list()
    else:
        values = res
    if not isinstance(values, list):
        values = [values]
    for v in values:
        _sample_pairs_rows.append({"target": target[0] if isinstance(target, tuple) and len(target) == 1 else target, "sample_pairs": v})

sample_pairs = pl.DataFrame(_sample_pairs_rows).explode("sample_pairs").drop_nulls(subset=["sample_pairs"])
sample_pairs = pl.concat([sample_pairs, taxonomy], how="horizontal")
sample_pairs = sample_pairs.with_columns(
    pl.col("taxonomy").map_elements(get_taxa_group, return_dtype=pl.Null).alias("taxa_group")
)
sample_pairs = sample_pairs.drop_nulls(subset=["taxa_group"])