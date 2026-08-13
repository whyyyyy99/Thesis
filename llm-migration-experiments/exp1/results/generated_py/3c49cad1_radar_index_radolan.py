import polars as pl

file_index = file_index.filter(
    pl.col("filename").str.contains("/bin/")
    & (
        pl.col("filename").str.ends_with(Extension.GZ.value)
        | pl.col("filename").str.ends_with(Extension.TAR_GZ.value)
    )
).clone()
