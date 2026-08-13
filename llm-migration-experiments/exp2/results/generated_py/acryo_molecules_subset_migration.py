if self._features is None:
    return self.__class__(pos, Rotation(quat))
return self.__class__(pos, Rotation(quat), self._features[spec, :])