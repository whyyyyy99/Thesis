import polars as pl

base_dfs = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for epoch, (train_index, test_index) in enumerate(skf.split(ds.X, ds.y)):
    _train_ds = cds.Dataset(
        df=ds.to_pandas().iloc[train_index],
        x_columns=ds.x_columns,
        y_columns=ds.y_columns,
        w_columns=ds.w_columns,
    )
    test_ds = cds.Dataset(
        df=ds.to_pandas().iloc[test_index],
        x_columns=ds.x_columns,
        y_columns=ds.y_columns,
        w_columns=ds.w_columns,
    )
    test_y = test_ds.y.with_row_index("index").rename({test_ds.y_columns[0]: "y"})
    test_w = test_ds.w.with_row_index("index").rename({test_ds.w_columns[0]: "w"})
    _pred_df = pl.DataFrame(
        {"index": test_y["index"], "pred": pred.reshape(-1)}
    )
    _base_df = test_y.join(test_w, on="index", how="inner")
    _base_df = _base_df.join(_pred_df, on="index", how="inner")
    base_dfs.append(_base_df)
base_df = pl.concat(base_dfs)
