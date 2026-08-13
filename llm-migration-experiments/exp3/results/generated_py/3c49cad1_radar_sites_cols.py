import polars as pl

data = data.drop(["coordinates_wgs84_text", "coordinates_gauss"])
data = data.rename({"coordinates_wgs84": "latitude"})
data.insert_column(4, pl.Series("longitude", seconds["coordinates_wgs84"].to_numpy()))
for column in ["latitude", "longitude"]:
    data = data.with_columns(
        pl.col(column)
        .cast(pl.Utf8)
        .str.strip_chars("NE")
        .str.replace(",", ".")
        .cast(pl.Float64)
        .alias(column)
    )
for column in ["wmo_id", "altitude"]:
    data = data.with_columns(pl.col(column).cast(pl.Int64).alias(column))
