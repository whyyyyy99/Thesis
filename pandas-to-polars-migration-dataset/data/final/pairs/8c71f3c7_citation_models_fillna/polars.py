    return df.with_columns(
        publication_date_rank=pl.when(pl.col("publication_date_rank").is_null())
        .then(len(df))
        .otherwise(pl.col("publication_date_rank"))
    )
