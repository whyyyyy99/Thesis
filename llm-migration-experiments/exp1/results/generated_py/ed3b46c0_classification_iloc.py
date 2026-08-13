import polars as pl

train_X = ds.X[train_idx]
train_y = ds.y[train_idx].to_numpy().reshape(-1)
valid_X = ds.X[valid_idx]
valid_w = ds.w[valid_idx].to_numpy().reshape(-1)
valid_y = ds.y[valid_idx].to_numpy().reshape(-1)
