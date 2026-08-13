import polars as pl

return pl.read_csv(self.mane_data_path, separator="\t")