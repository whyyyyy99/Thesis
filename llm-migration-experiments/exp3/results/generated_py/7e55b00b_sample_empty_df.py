import polars as pl


def sample(
    ds: Dataset, n: int | None = None, frac: float | None = None, random_state: int = 42
) -> Dataset:
    if n == 0 or frac == 0:
        return Dataset(
            pl.DataFrame(schema={col: pl.Null for col in ds.to_polars().columns}),
            ds.x_columns,
            ds.y_columns,
            ds.w_columns,
        )

    if n is None and frac is None:
        df = ds.to_polars().sample(n=1, seed=random_state)
    elif frac is not None:
        df = ds.to_polars().sample(fraction=frac, seed=random_state)
    else:
        df = ds.to_polars().sample(n=n, seed=random_state)

    return Dataset(df, ds.x_columns, ds.y_columns, ds.w_columns)
