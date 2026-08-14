import polars as pl

    base_dfs: list[pl.DataFrame] = []
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for epoch, (train_index, test_index) in enumerate(skf.split(ds.X, ds.y)):
        _train_ds = cds.Dataset(
            df=ds.to_frame()
            .with_row_index()
            .filter(pl.col("index").is_in(train_index))
            .drop("index"),
            x_columns=ds.x_columns,
            y_columns=ds.y_columns,
            w_columns=ds.w_columns,
        )
        test_ds = cds.Dataset(
            df=ds.to_frame()
            .with_row_index()
            .filter(pl.col("index").is_in(test_index))
            .drop("index"),
            x_columns=ds.x_columns,
            y_columns=ds.y_columns,
            w_columns=ds.w_columns,
        )
        _base_df = pl.DataFrame(
            {
                "pred": pred.reshape(-1),
                "y": test_ds.y,
                "W": test_ds.w,
            }
        )
        base_dfs.append(_base_df)
    base_df = pl.concat(base_dfs)
