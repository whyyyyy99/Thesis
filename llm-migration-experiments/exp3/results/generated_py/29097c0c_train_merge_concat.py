import polars as pl

_pred_df = pl.DataFrame(
    {"__index__": range(len(pred.reshape(-1))), "pred": pred.reshape(-1)}
)
_base_df = (
    test_ds.y.rename({test_ds.y_columns[0]: "y"})
    .with_row_index("__index__")
    .join(
        test_ds.w.rename({test_ds.w_columns[0]: "w"}).with_row_index("__index__"),
        on="__index__",
        how="inner",
    )
    .join(_pred_df, on="__index__", how="inner")
    .drop("__index__")
)
base_dfs.append(_base_df)
base_df = pl.concat(base_dfs)
