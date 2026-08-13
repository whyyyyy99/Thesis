import polars as pl

assert all(pl.Series(by).is_in(self.data.columns).to_list()), \
