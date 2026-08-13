import polars as pl

return pl.Series([i.text for i in timesteps.getchildren()]).str.to_datetime(strict=False)
