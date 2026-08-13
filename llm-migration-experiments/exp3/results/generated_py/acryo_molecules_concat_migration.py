import numpy as np
import polars as pl
from scipy.spatial.transform import Rotation


@classmethod
def concat(cls, moles: Iterable[Molecules], concat_features: bool = True) -> Self:
    """Concatenate Molecules objects."""
    pos: list[np.ndarray] = []
    quat: list[np.ndarray] = []
    features: list[pl.DataFrame] = []
    for mol in moles:
        pos.append(mol.pos)
        quat.append(mol.quaternion())
        features.append(mol.features)

    all_pos = np.concatenate(pos, axis=0)
    all_quat = np.concatenate(quat, axis=0)
    if concat_features:
        all_features = pl.concat(features, how="vertical")
    else:
        all_features = None

    return cls(all_pos, Rotation(all_quat), features=all_features)
