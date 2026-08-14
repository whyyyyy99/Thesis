import pandas as pd

        _pred_df = pd.DataFrame(
            {"index": test_ds.y.index, "pred": pred.reshape(-1)}
        ).set_index("index")
        _base_df = pd.merge(
            test_ds.y.rename(columns={test_ds.y_columns[0]: "y"}),
            test_ds.w.rename(columns={test_ds.w_columns[0]: "w"}),
            left_index=True,
            right_index=True,
        )
        _base_df = pd.merge(
            _base_df,
            _pred_df,
            left_index=True,
            right_index=True,
        )
        base_dfs.append(_base_df)
    base_df = pd.concat(base_dfs)
