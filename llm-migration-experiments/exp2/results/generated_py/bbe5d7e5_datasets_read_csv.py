import polars as pl


def func(stream):
    df = pl.read_csv(
        stream,
        try_parse_dates=True,
        schema_overrides={
            "pol_num": pl.Int64,
            "status": pl.Categorical,
        },
    )
    if df.width > 0:
        df = df.drop(df.columns[0])
    return df