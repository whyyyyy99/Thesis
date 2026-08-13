import polars as pl
import pandas as pd

base_dfs = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for epoch, (train_index, test_index) in enumerate(skf.split(ds.X, ds.y)):
    df = pl.from_pandas(ds.to_pandas().reset_index())
    _train_df = df.take(train_index)
    _train_ds = cds.Dataset(
        df=_train_df,
        x_columns=ds.x_columns,
        y_columns=ds.y_columns,
        w_columns=ds.w_columns,
    )
    test_df = df.take(test_index)
    test_ds = cds.Dataset(
        df=test_df,
        x_columns=ds.x_columns,
        y_columns=ds.y_columns,
        w_columns=ds.w_columns,
    )
    _pred_df = pl.DataFrame(
        {"index": test_df["index"], "pred": pred.reshape(-1)}
    )
    _base_df = test_df.select(
        [
            pl.col(test_ds.y_columns[0]).alias("y"),
            pl.col(test_ds.w_columns[0]).alias("w"),
            pl.col("index"),
        ]
    )
    _base_df = _base_df.join(_pred_df, on="index", how="inner")
    base_dfs.append(_base_df)
base_df = pl.concat(base_dfs)
