import pandas as pd
import polars as pl

_sample_pairs_rows = []
for _target in unbinned.get_column("target").unique(maintain_order=True).to_list():
    if _target is None:
        _group = unbinned.filter(pl.col("target").is_null())
    else:
        _group = unbinned.filter(pl.col("target") == _target)
    _result = find_pairs(_group.to_pandas())
    _sample_pairs_rows.append({"target": _target, "sample_pairs": _result})

sample_pairs = pl.DataFrame(_sample_pairs_rows)
sample_pairs = (
    sample_pairs
    .explode("sample_pairs")
    .drop_nulls(subset="sample_pairs")
    .join(taxonomy, on="target", how="left")
)
sample_pairs = sample_pairs.with_columns(
    pl.col("taxonomy").map_elements(get_taxa_group, return_dtype=pl.Object).alias("taxa_group")
)
sample_pairs = sample_pairs.drop_nulls(subset="taxa_group")
