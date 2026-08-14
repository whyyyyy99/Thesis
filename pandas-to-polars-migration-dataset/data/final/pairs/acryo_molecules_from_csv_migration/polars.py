def from_csv(
    cls,
    path: PathLike,
    pos_cols: list[str] = ["z", "y", "x"],
    rot_cols: list[str] = ["zvec", "yvec", "xvec"],
    **pl_kwargs,
) -> Self:
    import polars as pl
    pos_cols = pos_cols.copy()
    rot_cols = rot_cols.copy()
    df = pl.read_csv(path, **pl_kwargs)
    pos = df.select(pos_cols)
    rotvec = df.select(rot_cols)
    cols = pos.columns + rotvec.columns
    others = df.select([c for c in df.columns if c not in cols])
    return cls(
        np.asarray(pos).T,
        Rotation.from_rotvec(np.asarray(rotvec).T),
        features=others,
    )
