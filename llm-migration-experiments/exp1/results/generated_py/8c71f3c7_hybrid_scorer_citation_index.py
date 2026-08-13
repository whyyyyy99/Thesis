import polars as pl

citation_to_language_candidate_ids: pl.Series
...
        self.citation_to_language_candidate_ids = pl.Series(
            self.citation_to_language_candidates.height
        )
