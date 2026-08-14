import pandas as pd

def get_regular_df(start_date, end_date, exclude_stations):
    request = stations.filter_by_distance(latlon=(50.0, 8.9), distance=30)
    df = request.values.all().df.dropna()
    station_ids = df.station_id.tolist()
    first_station_id = set(station_ids).difference(set(exclude_stations)).pop()
    return df[df["station_id"] == first_station_id]
