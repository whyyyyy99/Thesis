        scaling_factors_df = polars.concat(scaling_factors_dfs)
        ensemble.save_observation_scaling_factors(scaling_factors_df)
