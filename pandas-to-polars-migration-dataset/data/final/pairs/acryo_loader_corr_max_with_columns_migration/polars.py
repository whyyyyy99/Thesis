feature_list = get_feature_list(corr_max, local_shifts, rotator.as_rotvec())
mole_aligned.features = self.molecules.features.with_columns(
    feature_list + pl.Series("labels", labels)
)
