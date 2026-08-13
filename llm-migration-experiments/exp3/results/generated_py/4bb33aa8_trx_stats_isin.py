import polars as pl

assert all(item in old_self.data.columns for item in by), \
