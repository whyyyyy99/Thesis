import pandas as pd

        pred_df = pd.DataFrame(
            {"index": ds.y.index[valid_idx], "pred": pred}
        ).set_index("index")
        base_dfs.append(
            pd.merge(
                pred_df,
                base_df,
                left_index=True,
                right_index=True,
            )
        )
    base_df = pd.concat(base_dfs)
    _metrics = {
        "roc_auc": roc_auc_score(base_df.y, base_df.pred),
        "accuracy": accuracy_score(base_df.y, base_df.pred > 0.5),
        "precision": precision_score(base_df.y, base_df.pred > 0.5),
        "recall": recall_score(base_df.y, base_df.pred > 0.5),
        "f1": f1_score(base_df.y, base_df.pred > 0.5),
    }
