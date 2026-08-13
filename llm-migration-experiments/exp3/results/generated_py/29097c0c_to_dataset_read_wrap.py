import polars as pl

def make_lenta() -> None:
    pathlinker = path_linker("lenta")
    df = pl.read_csv(pathlinker.origin)
    df = onehot_encoding(df, ["gender"])
    df = df.fill_null(0).fill_nan(0)
    df = df.with_columns(
        pl.col("group").replace({"test": 1, "control": 0}, default=None)
    )
    y_columns = ["response_att"]
    w_columns = ["group"]
    x_columns = [column for column in df.columns if column not in y_columns + w_columns]
    ds = Dataset(df, x_columns, y_columns, w_columns)
    ds.save(pathlinker.base)
