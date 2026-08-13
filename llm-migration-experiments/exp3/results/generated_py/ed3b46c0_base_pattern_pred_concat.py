import polars as pl

_pred_dfs.append(
    pl.DataFrame(
        {"index": ds.y.index[valid_idx], "pred": pred.reshape(-1)}
    )
)
pred_df = pl.concat(_pred_dfs, how="vertical")
base_df = pl.from_pandas(
    pl.from_pandas(ds.y.rename(...).to_frame(), include_index=True).to_pandas(),
    include_index=True,
).join(
    pl.from_pandas(ds.w.rename(...).to_frame(), include_index=True),
    on="index",
    how="inner",
)
output_df = base_df.join(pred_df, on="index", how="inner")
