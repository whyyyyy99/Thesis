import polars as pl

def sample(
    ds: Dataset, n: int | None = None, frac: float | None = None, random_state: int = 42
) -> Dataset:
    if n == 0 or frac == 0:
        _df = ds.to_frame()
        return Dataset(
            pl.DataFrame(schema=_df.schema),
            ds.x_columns,
            ds.y_columns,
            ds.w_columns,
        )

    df = ds.to_frame().sample(n=n, fraction=frac, seed=random_state)
    return Dataset(df, ds.x_columns, ds.y_columns, ds.w_columns)
