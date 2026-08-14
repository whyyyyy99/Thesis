    df_fileindex = df_fileindex.filter(
        pl.col("filename").str.contains("/bin/", literal=True)
        & (pl.col("filename").str.ends_with(Extension.GZ.value) | pl.col("filename").str.ends_with(Extension.TAR.value))
    )
