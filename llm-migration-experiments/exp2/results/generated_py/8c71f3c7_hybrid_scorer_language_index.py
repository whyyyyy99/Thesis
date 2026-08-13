import polars as pl

        self.language_to_citation_candidate_ids = pl.Series(
            "index", range(self.language_to_citation_candidates.height)
        )