mole_aligned.features = self.molecules.features.with_columns(
    get_feature_list(scores, local_shifts, rotator.as_rotvec()),
)
