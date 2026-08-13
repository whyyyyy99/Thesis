import polars as pl

return pl.DataFrame(
    {"scores": [sort_document_scores(common_citations_scores)]}
)
