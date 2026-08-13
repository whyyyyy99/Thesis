import polars as pl
from collections.abc import Iterable

_by_values = [by] if isinstance(by, (str, bytes)) or not isinstance(by, Iterable) else by
assert pl.Series(_by_values).is_in(old_self.data.columns).all()
