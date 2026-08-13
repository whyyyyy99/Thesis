import numpy as np
import polars as pl

n_real = len(realizations)
data = np.vstack([obs_vals, std_vals, resp_vals.reshape(n_real, -1)])
return (
    pl.DataFrame(
        data,
        schema=[str(col) for col in index_vals],
        orient="row",
    )
    .with_columns(pl.Series("index", ["OBS", "STD", *realizations]))
    .select(["index", *[str(col) for col in index_vals]])
)