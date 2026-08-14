import pandas as pd

        oar = observation.merge(all_responses, on=["realization"], how="left")
    return {
        "obs_keys_count": len(oar["observations"]),
        "obs_values":     oar["observations"].values.ravel(),
        "obs_errors":     oar["std"].values.ravel(),
        "n_reals":        len(oar["realization"]),
    }
