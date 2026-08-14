import polars as pl

        _base_df = pl.DataFrame(
            {
                "pred": pred.reshape(-1),
                "y": test_ds.y,
                "W": test_ds.w,
            }
        )
        base_dfs.append(_base_df)
    base_df = pl.concat(base_dfs)
