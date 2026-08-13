import polars as pl
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

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
    "roc_auc": roc_auc_score(base_df["y"].to_numpy(), base_df["pred"].to_numpy()),
    "accuracy": accuracy_score(base_df["y"].to_numpy(), (base_df["pred"] > 0.5).to_numpy()),
    "precision": precision_score(base_df["y"].to_numpy(), (base_df["pred"] > 0.5).to_numpy()),
    "recall": recall_score(base_df["y"].to_numpy(), (base_df["pred"] > 0.5).to_numpy()),
    "f1": f1_score(base_df["y"].to_numpy(), (base_df["pred"] > 0.5).to_numpy()),
}