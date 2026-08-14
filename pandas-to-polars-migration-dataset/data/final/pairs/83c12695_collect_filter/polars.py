    appraise_binned = appraise_binned.with_columns(
        pl.col("sample").str.replace("\.1$", "")
    ).filter(
        pl.col("sample") == sample
    )
