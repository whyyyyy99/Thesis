import polars as pl

df = pl.read_csv(
    stream,
    schema_overrides={
        "pol_num": pl.Int64,
        "status": pl.Categorical,
    },
    try_parse_dates=True,
)

if df.width > 0:
    df = df.drop(df.columns[0])

return df
