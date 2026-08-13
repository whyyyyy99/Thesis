import pandas as pd
import polars as pl

scaling_factors_df = pl.concat(scaling_factors_dfs, how="vertical")
ensemble.save_observation_scaling_factors(
    scaling_factors_df.to_pandas().set_index(
        ["input_group", "obs_key", "index"], verify_integrity=True
    ).to_xarray()
)
