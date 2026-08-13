import pandas as pd
import polars as pl

scaling_factors_df = pl.concat(scaling_factors_dfs, how="vertical").to_pandas()
if scaling_factors_df.duplicated(subset=["input_group", "obs_key", "index"]).any():
    raise ValueError("Index has duplicate keys")

scaling_factors_df = scaling_factors_df.set_index(
    ["input_group", "obs_key", "index"], verify_integrity=True
)
ensemble.save_observation_scaling_factors(scaling_factors_df.to_xarray())