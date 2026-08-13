if features is not None:
    features = features.clone()
out = self.__class__(coords, self._rotator, features=features)
