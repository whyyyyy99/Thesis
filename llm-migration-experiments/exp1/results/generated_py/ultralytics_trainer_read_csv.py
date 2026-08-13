import polars as pl

return pl.read_csv(self.csv).to_dict(as_series=False)
