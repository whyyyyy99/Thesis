import polars as pl

if self._features is None:
    return self.__class__(pos, Rotation(quat))
return self.__class__(
    pos,
    Rotation(quat),
    self._features.slice(spec, 1) if isinstance(spec, int) else self._features.slice(
        spec.start or 0,
        (spec.stop - (spec.start or 0)) if spec.stop is not None else self._features.height - (spec.start or 0),
    ),
)
