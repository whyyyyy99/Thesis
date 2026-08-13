import polars as pl

        _pred_df = pl.DataFrame(
            {"index": test_ds.y.index.to_list(), "pred": pred.reshape(-1).tolist()}
        )
        _base_df = pl.DataFrame(
            {
                "index": test_ds.y.index.to_list(),
                **{col: test_ds.y[col].to_list() for col in test_ds.y.columns},
            }
        ).rename({test_ds.y_columns[0]: "y"})
        _base_df = _base_df.join(
            pl.DataFrame(
                {
                    "index": test_ds.w.index.to_list(),
                    **{col: test_ds.w[col].to_list() for col in test_ds.w.columns},
                }
            ).rename({test_ds.w_columns[0]: "w"}),
            on="index",
            how="inner",
        )
        _base_df = _base_df.join(_pred_df, on="index", how="inner")
        base_dfs.append(_base_df)
    base_df = pl.concat(base_dfs)
