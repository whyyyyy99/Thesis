import pandas as pd

        train_X = ds.X.iloc[train_idx]
        train_y = ds.y.iloc[train_idx].to_numpy().reshape(-1)
        valid_X = ds.X.iloc[valid_idx]
        valid_w = ds.w.iloc[valid_idx].to_numpy().reshape(-1)
        valid_y = ds.y.iloc[valid_idx].to_numpy().reshape(-1)
