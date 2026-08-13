import polars as pl

df = pl.read_csv(
    stream,
    schema_overrides={"age": pl.Int64, "qx": pl.Float64, "gender": pl.Utf8},
)
if df.width > 0:
    df = df.select(df.columns[1:])
df
