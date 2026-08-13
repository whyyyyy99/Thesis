import polars as pl

self.citation_to_language_candidate_ids = pl.Series(
    "index", range(self.citation_to_language_candidates.height)
)