import polars as pl

assert pl.Series(by).is_in(self.data.columns).all(), \