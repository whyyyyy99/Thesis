import polars as pl

def make_lenta() -> None:
    pathlinker = path_linker("lenta")
    df = pl.read_csv(pathlinker.origin)
    df = onehot_encoding(df, ["gender"])
    df = df.fill_null(0)
    df = df.with_columns(
        pl.when(pl.col("group") == "test")
        .then(1)
        .when(pl.col("group") == "control")
        .then(0)
        .otherwise(None)
        .alias("group")
    )
    y_columns = ["response_att"]
    w_columns = ["group"]
    x_columns = [column for column in df.columns if column not in y_columns + w_columns]
    ds = Dataset(df, x_columns, y_columns, w_columns)
    ds.save(pathlinker.base)