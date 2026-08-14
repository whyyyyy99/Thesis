import polars as pl
import pandas as pd

def make_lenta() -> None:
    pathlinker = path_linker("lenta")
    df = pd.read_parquet(pathlinker.lake)
    df = onehot_encoding(df, ["gender"])
    df = df.fillna(0)
    df["group"] = df["group"].apply(lambda x: {"test": 1, "control": 0}.get(x))
    y_columns = ["response_att"]
    w_columns = ["group"]
    x_columns = [column for column in df.columns if column not in y_columns + w_columns]
    ds = Dataset(pl.DataFrame(df), x_columns, y_columns, w_columns)
    ds.save(pathlinker.mart)
