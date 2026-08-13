import polars as pl

df = df.drop_nulls()
df = df.filter(
    pl.all_horizontal(
        [
            pl.col(c).is_not_nan() if df.schema[c] in (pl.Float32, pl.Float64) else pl.col(c).is_not_null()
            for c in df.columns
        ]
    )
)
station_ids = df["station_id"].to_list()
first_station_id = station_ids[0]
return df.filter(pl.col("station_id") == first_station_id)
