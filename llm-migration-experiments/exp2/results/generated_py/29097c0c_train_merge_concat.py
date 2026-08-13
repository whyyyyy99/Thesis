import polars as pl

_pred_df = pl.DataFrame(
    {"index": test_ds.y.index, "pred": pred.reshape(-1)}
)
_base_df = (
    pl.from_pandas(test_ds.y.reset_index())
    .rename({test_ds.y.reset_index().columns[0]: "index", test_ds.y_columns[0]: "y"})
    .join(
        pl.from_pandas(test_ds.w.reset_index()).rename(
            {test_ds.w.reset_index().columns[0]: "index", test_ds.w_columns[0]: "w"}
        ),
        on="index",
        how="inner",
    )
    .join(_pred_df, on="index", how="inner")
    .select(["y", "w", "pred"])
)
base_dfs.append(_base_df)
base_df = pl.concat(base_dfs)