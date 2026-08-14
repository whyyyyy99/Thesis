def get_features(corr_max, local_shifts, rotvec) -> pl.DataFrame:

    features = {
        "score": corr_max,
        "shift-z": np.round(local_shifts[:, 0], 2),
        "shift-y": np.round(local_shifts[:, 1], 2),
        "shift-x": np.round(local_shifts[:, 2], 2),
        "rotvec-z": np.round(rotvec[:, 0], 5),
        "rotvec-y": np.round(rotvec[:, 1], 5),
        "rotvec-x": np.round(rotvec[:, 2], 5),
    }
    return pl.DataFrame(features)


def get_feature_list(corr_max, local_shifts, rotvec) -> list[pl.Series]:

    features = [
        pl.Series("score", corr_max),
        pl.Series("shift-z", np.round(local_shifts[:, 0], 2)),
        pl.Series("shift-y", np.round(local_shifts[:, 1], 2)),
        pl.Series("shift-x", np.round(local_shifts[:, 2], 2)),
        pl.Series("rotvec-z", np.round(rotvec[:, 0], 5)),
        pl.Series("rotvec-y", np.round(rotvec[:, 1], 5)),
        pl.Series("rotvec-x", np.round(rotvec[:, 2], 5)),
    ]
    return features
