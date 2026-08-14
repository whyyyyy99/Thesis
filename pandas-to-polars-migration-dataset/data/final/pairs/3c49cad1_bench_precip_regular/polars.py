import polars as pl

def get_regular_df(start_date, end_date, exclude_stations):
    request = stations.filter_by_distance(latlon=(50.0, 8.9), distance=30)
    df = request.values.all().df.drop_nulls()
    station_ids = df.get_column("station_id")
    first_station_id = set(station_ids).difference(set(exclude_stations)).pop()
    return df.filter(pl.col("station_id").eq(first_station_id))
