import pandas as pd

        _pred_dfs.append(
            pd.DataFrame(
                {"index": ds.y.index[valid_idx], "pred": pred.reshape(-1)}
            ).set_index("index")
        )
    pred_df = pd.concat(_pred_dfs, axis=0)
    base_df = pd.merge(ds.y.rename(...), ds.w.rename(...), left_index=True, right_index=True)
    output_df = pd.merge(base_df, pred_df, left_index=True, right_index=True)
