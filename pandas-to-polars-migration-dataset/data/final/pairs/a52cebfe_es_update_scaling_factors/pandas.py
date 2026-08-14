import pandas as pd

        scaling_factors_df = pd.concat(scaling_factors_dfs).set_index(
            ["input_group", "obs_key", "index"], verify_integrity=True
        )
        ensemble.save_observation_scaling_factors(scaling_factors_df.to_xarray())
