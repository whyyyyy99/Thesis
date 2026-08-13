import polars as pl

df = pl.read_csv(
    stream,
    try_parse_dates=True,
    schema_overrides={
        "pol_num": pl.Int64,
        "status": pl.Categorical,
    },
)

if df.width > 0:
    df = df.select(df.columns[1:])

return df
