mole_aligned.features = update_features(
    self.molecules.features.clone(),
    get_features(scores, local_shifts, rotator.as_rotvec()),
)
