import polars as pl

def split(
    ds: Dataset,
    test_frac: float | None = None,
    test_n: float | None = None,
    random_state: int = 42,
) -> tuple[Dataset, Dataset]:
    if test_frac == 0 or test_n == 0:
        return ds, Dataset(
            pl.DataFrame(schema=ds.to_frame().schema),
            ds.x_columns,
            ds.y_columns,
            ds.w_columns,
        )
    if test_frac == 1 or test_n == len(ds):
        return Dataset(
            pl.DataFrame(schema=ds.to_frame().schema),
            ds.x_columns,
            ds.y_columns,
            ds.w_columns,
        ), ds

    test_size = test_frac if test_frac is not None else test_n
    train_df, test_df = train_test_split(
        ds.to_frame(), test_size=test_size, random_state=random_state
    )
    return (
        Dataset(train_df, ds.x_columns, ds.y_columns, ds.w_columns),
        Dataset(test_df, ds.x_columns, ds.y_columns, ds.w_columns),
    )
