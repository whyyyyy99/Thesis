import polars as pl

mole_aligned.features = pl.concat(
    [
        self.molecules.features,
        get_features(corr_max, local_shifts, rotator.as_rotvec()),
        pl.DataFrame({"labels": labels}),
    ],
    how="horizontal",
)
