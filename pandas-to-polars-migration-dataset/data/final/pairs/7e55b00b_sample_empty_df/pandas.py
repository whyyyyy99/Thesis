import pandas as pd

def sample(
    ds: Dataset, n: int | None = None, frac: float | None = None, random_state: int = 42
) -> Dataset:
    if n == 0 or frac == 0:
        return Dataset(
            pd.DataFrame(columns=ds.to_pandas().columns),
            ds.x_columns,
            ds.y_columns,
            ds.w_columns,
        )

    df = ds.to_pandas().sample(n=n, frac=frac, random_state=random_state)
    return Dataset(df, ds.x_columns, ds.y_columns, ds.w_columns)
