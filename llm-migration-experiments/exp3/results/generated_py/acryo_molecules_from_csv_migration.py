import polars as pl


def from_csv(
    cls,
    path: str,
    pos_cols: list[str] = ["z", "y", "x"],
    rot_cols: list[str] = ["zvec", "yvec", "xvec"],
    **pd_kwargs,
) -> Self:
    pos_cols = pos_cols.copy()
    rot_cols = rot_cols.copy()
    df: pl.DataFrame = pl.read_csv(path, **pd_kwargs)
    pos = df.select(pos_cols)
    rotvec = df.select(rot_cols)
    cols = pos_cols + rot_cols
    others = df.select([c for c in df.columns if c not in cols])
    return cls(
        pos,
        Rotation.from_rotvec(rotvec),
        features=others,
    )
