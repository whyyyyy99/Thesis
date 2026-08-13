import polars as pl

appraise_binned = appraise_binned.with_columns(
    pl.col("sample").str.replace(r"\.1$", "", literal=False).alias("sample")
)
appraise_binned = appraise_binned.filter(pl.col("sample") == sample)
