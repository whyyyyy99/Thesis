import polars as pl

data = data.drop(["coordinates_wgs84_text", "coordinates_gauss"])
data = data.rename({"coordinates_wgs84": "latitude"})
data.insert_column(4, pl.Series("longitude", seconds["coordinates_wgs84"]))
data = data.with_columns(
    [
        pl.col("latitude")
        .cast(pl.Utf8)
        .str.strip_chars("NE")
        .str.replace(",", ".", literal=True)
        .cast(pl.Float64),
        pl.col("longitude")
        .cast(pl.Utf8)
        .str.strip_chars("NE")
        .str.replace(",", ".", literal=True)
        .cast(pl.Float64),
        pl.col("wmo_id").cast(pl.Int64),
        pl.col("altitude").cast(pl.Int64),
    ]
)