import polars as pl

df = pl.read_csv(
    stream,
    schema_overrides={
        "age": pl.Int64,
        "qx": pl.Float64,
        "gender": pl.Utf8,
    },
)

return df.drop(df.columns[0]) if df.columns else df