if features is not None:
    features = pl.DataFrame(list(features))
out = self.__class__(self._pos, rot, features=features)
