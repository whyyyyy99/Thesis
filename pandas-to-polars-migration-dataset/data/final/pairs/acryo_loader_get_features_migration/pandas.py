def get_features(corr_max, local_shifts, rotvec) -> pd.DataFrame:
    import pandas as pd

    features = {
        "score": corr_max,
        "shift-z": np.round(local_shifts[:, 0], 2),
        "shift-y": np.round(local_shifts[:, 1], 2),
        "shift-x": np.round(local_shifts[:, 2], 2),
        "rotvec-z": np.round(rotvec[:, 0], 5),
        "rotvec-y": np.round(rotvec[:, 1], 5),
        "rotvec-x": np.round(rotvec[:, 2], 5),
    }
    return pd.DataFrame(features)
