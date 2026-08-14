import pandas as pd


            n_real = len(realizations)
    data = np.vstack([obs_vals, std_vals, resp_vals.reshape(n_real, -1)])
    return pd.DataFrame(
        data,
        index=("OBS", "STD", *realizations),
        columns=pd.MultiIndex.from_tuples(index_vals),
    )
