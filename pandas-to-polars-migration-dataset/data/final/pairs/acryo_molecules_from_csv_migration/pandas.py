def from_csv(
    cls,
    path: str,
    pos_cols: list[str] = ["z", "y", "x"],
    rot_cols: list[str] = ["zvec", "yvec", "xvec"],
    **pd_kwargs,
) -> Self:
    import pandas as pd
    pos_cols = pos_cols.copy()
    rot_cols = rot_cols.copy()
    df: pd.DataFrame = pd.read_csv(path, **pd_kwargs)  # type: ignore
    pos = df[pos_cols]
    rotvec = df[rot_cols]
    cols = pos + rotvec
    others = df.iloc[:, np.array([c not in cols for c in df.columns])]
    return cls(
        pos,
        Rotation.from_rotvec(rotvec),
        features=others,
    )
