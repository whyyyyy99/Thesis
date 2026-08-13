import polars as pl

train_X = ds.X.take(train_idx)
train_y = ds.y.take(train_idx).to_numpy().reshape(-1)
valid_X = ds.X.take(valid_idx)
valid_w = ds.w.take(valid_idx).to_numpy().reshape(-1)
valid_y = ds.y.take(valid_idx).to_numpy().reshape(-1)
