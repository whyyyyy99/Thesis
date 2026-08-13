import polars as pl

        _pred_dfs.append(
            pl.DataFrame(
                {"index": ds.y.index[valid_idx], "pred": pred.reshape(-1)}
            )
        )
    pred_df = pl.concat(_pred_dfs, how="vertical")
    base_df = pl.concat(
        [
            pl.from_pandas(ds.y.rename(...).reset_index()),
            pl.from_pandas(ds.w.rename(...).reset_index()),
        ],
        how="horizontal",
    )
    output_df = base_df.join(pred_df, on="index", how="inner")
