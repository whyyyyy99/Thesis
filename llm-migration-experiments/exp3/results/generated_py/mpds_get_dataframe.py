import polars as pl

return pl.DataFrame(self.get_data(*args, **kwargs), schema=columns)
