    df = pl.DataFrame({primary_key.name: primary_key, score.name: score})
    df = df.sort(by=str(score.name), descending=descending)
    df = df.with_columns(
        pl.Series(
            name="rank",
            values=np.ceil(np.arange(1, len(df) + 1) / len(df) * k),
            dtype=pl.Int64,
        )
    )
