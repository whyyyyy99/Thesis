df = df.drop_nulls()
station_ids = df.get_column("station_id").to_list()
first_station_id = station_ids[0]
return df.filter(pl.col("station_id") == first_station_id)