import polars as pl

        base_dfs.append(pl.DataFrame({"pred": pred, "y": valid_y, "w": valid_w}))
    base_df = pl.concat(base_dfs)
    _metrics = {
        "roc_auc": roc_auc_score(base_df["y"], base_df["pred"]),
        "accuracy": accuracy_score(base_df["y"], base_df["pred"] > 0.5),
        "precision": precision_score(base_df["y"], base_df["pred"] > 0.5),
        "recall": recall_score(base_df["y"], base_df["pred"] > 0.5),
        "f1": f1_score(base_df["y"], base_df["pred"] > 0.5),
    }
