import polars as pl
import numpy as np

n_real = len(realizations)
data = np.vstack([obs_vals, std_vals, resp_vals.reshape(n_real, -1)])
return pl.DataFrame(
    data,
    schema=[str(col) for col in index_vals],
)
