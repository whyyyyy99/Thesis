        data = data.drop(columns=["coordinates_wgs84_text", "coordinates_gauss"])
        data = data.rename(mapping={"coordinates_wgs84": "latitude"})
        data = data.with_columns(seconds.get_column("coordinates_wgs84").alias("longitude"))
        data = data.with_columns(
            pl.col("latitude").apply(lambda x: x.strip("NE").replace(",", ".")).cast(float),
            pl.col("longitude").apply(lambda x: x.strip("NE").replace(",", ".")).cast(float),
            pl.col("wmo_id").cast(int),
            pl.col("altitude").cast(int),
        )
