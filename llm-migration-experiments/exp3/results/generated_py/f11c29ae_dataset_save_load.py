import json
from pathlib import Path

import polars as pl


def save(self, path: Path) -> None:
    path.mkdir(exist_ok=True, parents=True)
    self.__df.write_csv(path / "data.csv")
    json.dump(
        {
            "x_columns": self.x_columns,
            "y_columns": self.y_columns,
            "w_columns": self.w_columns,
        },
        (path / "meta.json").open("w"),
    )


@classmethod
def load(cls, path: Path) -> "Dataset":
    data_path = path / "data.csv"
    meta_path = path / "meta.json"
    if (not data_path.exists()) or (not meta_path.exists()):
        raise FileNotFoundError()

    df = pl.read_csv(data_path)
    meta = json.load(meta_path.open(mode="r"))
    return cls(df, **meta)
