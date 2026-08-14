import pandas as pd

    station_ids = request.df["station_id"].values.tolist()
    latitudes = request.df["latitude"].values.tolist()
    longitudes = request.df["longitude"].values.tolist()
