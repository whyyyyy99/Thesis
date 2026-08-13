import polars as pl

df = df.drop_nulls()
nan_exprs = []
for c, dt in df.schema.items():
    if dt in pl.FLOAT_DTYPES:
        nan_exprs.append(pl.col(c).is_nan())
if nan_exprs:
    df = df.filter(~pl.any_horizontal(nan_exprs))
station_ids = df["station_id"].to_list()
first_station_id = station_ids[0]
return df.filter(pl.col("station_id") == first_station_id)
