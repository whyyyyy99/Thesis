import polars as pl

return df.with_columns(
    pl.col("publication_date").rank(descending=True).alias("publication_date_rank"),
    pl.col("citationcount_document").rank(descending=True).alias("citationcount_document_rank"),
    pl.col("citationcount_author").rank(descending=True).alias("citationcount_author_rank"),
)
