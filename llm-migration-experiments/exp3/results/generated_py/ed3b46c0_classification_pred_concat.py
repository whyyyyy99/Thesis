import polars as pl

pred_df = pl.DataFrame(
    {"index": ds.y.index[valid_idx], "pred": pred}
)
base_dfs.append(
    pred_df.join(
        base_df,
        on="index",
        how="inner",
    )
)
base_df = pl.concat(base_dfs)
_metrics = {
    "roc_auc": roc_auc_score(base_df["y"], base_df["pred"]),
    "accuracy": accuracy_score(base_df["y"], base_df["pred"] > 0.5),
    "precision": precision_score(base_df["y"], base_df["pred"] > 0.5),
    "recall": recall_score(base_df["y"], base_df["pred"] > 0.5),
    "f1": f1_score(base_df["y"], base_df["pred"] > 0.5),
}
