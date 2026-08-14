    df = request.values.all().df.drop_nulls()
    station_ids = df.get_column("station_id")
    ...
    return df.filter(pl.col("station_id").eq(first_station_id))
