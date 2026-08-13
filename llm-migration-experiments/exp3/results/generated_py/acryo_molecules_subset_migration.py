import polars as pl

if self._features is None:
    return self.__class__(pos, Rotation(quat))

if isinstance(spec, int):
    features = self._features.slice(spec, 1)
elif isinstance(spec, slice) and spec.step in (None, 1):
    start = 0 if spec.start is None else spec.start
    stop = self._features.height if spec.stop is None else spec.stop
    length = max(0, stop - start)
    features = self._features.slice(start, length)
else:
    features = pl.DataFrame(self._features.to_dicts()[spec])

return self.__class__(pos, Rotation(quat), features)
