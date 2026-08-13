import polars as pl

self.data = self.data.join(trx_data, on=["pol_num", date_cols[0]], how="left")
trx_cols = [x for x in self.data.columns if x.startswith("trx_")]
self.data = self.data.with_columns([pl.col(trx_cols).fill_null(0)])