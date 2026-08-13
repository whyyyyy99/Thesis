import polars as pl

return df.with_columns(
    pl.col("publication_date_rank").fill_null(len(df)).fill_nan(len(df)).alias("publication_date_rank")
)
