import polars as pl

base_dfs = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for epoch, (train_index, test_index) in enumerate(skf.split(ds.X, ds.y)):
    _train_ds = cds.Dataset(
        df=pl.from_pandas(ds.to_pandas().reset_index())[train_index, :].to_pandas().set_index("index"),
        x_columns=ds.x_columns,
        y_columns=ds.y_columns,
        w_columns=ds.w_columns,
    )
    test_df = pl.from_pandas(ds.to_pandas().reset_index())[test_index, :]
    test_ds = cds.Dataset(
        df=test_df.to_pandas().set_index("index"),
        x_columns=ds.x_columns,
        y_columns=ds.y_columns,
        w_columns=ds.w_columns,
    )
    _pred_df = pl.DataFrame(
        {"index": test_df["index"], "pred": pred.reshape(-1)}
    )
    _base_df = (
        pl.from_pandas(
            test_ds.y.rename(columns={test_ds.y_columns[0]: "y"}).reset_index()
        )
        .join(
            pl.from_pandas(
                test_ds.w.rename(columns={test_ds.w_columns[0]: "w"}).reset_index()
            ),
            on="index",
            how="inner",
        )
        .join(_pred_df, on="index", how="inner")
        .drop("index")
    )
    base_dfs.append(_base_df)
base_df = pl.concat(base_dfs)