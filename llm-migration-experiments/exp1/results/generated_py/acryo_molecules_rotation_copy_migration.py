if features is not None:
    features = features.clone()
out = self.__class__(self._pos, rot, features=features)
