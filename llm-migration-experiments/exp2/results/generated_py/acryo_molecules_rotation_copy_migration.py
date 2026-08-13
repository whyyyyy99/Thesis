if features is not None:
    features = features.clone() if hasattr(features, "clone") else features.copy()
out = self.__class__(self._pos, rot, features=features)