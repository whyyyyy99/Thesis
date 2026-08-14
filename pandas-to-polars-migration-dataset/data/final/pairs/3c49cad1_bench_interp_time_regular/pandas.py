import pandas as pd

    df = df.dropna()
    station_ids = df.station_id.tolist()
    first_station_id = station_ids[0]
    return df[df["station_id"] == first_station_id]
