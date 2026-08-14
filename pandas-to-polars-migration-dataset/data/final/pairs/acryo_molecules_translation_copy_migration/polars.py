if features is not None:
    features = pl.DataFrame(list(features))  # copy
out = self.__class__(coords, self._rotator, features=features)
