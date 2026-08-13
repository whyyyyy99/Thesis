import polars as pl

end_date = pl.Series([end_date]).cast(pl.Utf8).str.to_datetime().item()
start_date = pl.Series([start_date]).cast(pl.Utf8).str.to_datetime().item()