mole_aligned.features = pd.concat(
    [
        self.molecules.features,
        get_features(corr_max, local_shifts, rotator.as_rotvec()),
        pd.DataFrame({"labels": labels}),
    ],
    axis=1,
)
