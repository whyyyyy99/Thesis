import polars as pl

return pl.read_csv(
    stream,
    schema_overrides={
        "age": pl.Int64,
        "qx": pl.Float64,
        "gender": pl.Utf8,
    },
)[:, 1:]
