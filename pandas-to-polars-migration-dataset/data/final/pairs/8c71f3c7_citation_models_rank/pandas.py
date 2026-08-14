import pandas as pd

    return df.assign(
        publication_date_rank=df["publication_date"].rank(ascending=False),
        citationcount_document_rank=df["citationcount_document"].rank(ascending=False),
        citationcount_author_rank=df["citationcount_author"].rank(ascending=False),
    )
