import polars as pl

return df.with_columns(
    publication_date_rank=pl.col("publication_date").rank(method="average", descending=True),
    citationcount_document_rank=pl.col("citationcount_document").rank(method="average", descending=True),
    citationcount_author_rank=pl.col("citationcount_author").rank(method="average", descending=True),
)
