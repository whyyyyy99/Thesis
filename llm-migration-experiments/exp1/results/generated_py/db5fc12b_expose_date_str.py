import polars as pl

end_date = pl.select(pl.lit(end_date).cast(pl.Utf8).str.to_datetime()).item()
start_date = pl.select(pl.lit(start_date).cast(pl.Utf8).str.to_datetime()).item()
