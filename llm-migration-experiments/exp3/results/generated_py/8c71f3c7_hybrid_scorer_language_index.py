import polars as pl

    language_to_citation_candidate_ids: object
    ...
        self.language_to_citation_candidate_ids = self.language_to_citation_candidates.with_row_index().get_column("index")
