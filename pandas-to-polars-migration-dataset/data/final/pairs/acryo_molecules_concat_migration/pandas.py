@classmethod
def concat(cls, moles: Iterable[Molecules], concat_features: bool = True) -> Self:
    """Concatenate Molecules objects."""
    pos: list[np.ndarray] = []
    quat: list[np.ndarray] = []
    features: list[pd.DataFrame] = []
    for mol in moles:
        pos.append(mol.pos)
        quat.append(mol.quaternion())
        features.append(mol.features)

    all_pos = np.concatenate(pos, axis=0)
    all_quat = np.concatenate(quat, axis=0)
    if concat_features:
        import pandas as pd

        all_features = pd.concat(features, axis=0)
    else:
        all_features = None

    return cls(all_pos, Rotation(all_quat), features=all_features)
