import polars as pl

oar = observation.join(all_responses, on=["realization"], how="left")
return {
    "obs_keys_count": len(oar["observations"]),
    "obs_values":     oar["observations"].to_numpy().ravel(),
    "obs_errors":     oar["std"].to_numpy().ravel(),
    "n_reals":        len(oar["realization"]),
}
