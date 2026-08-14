    citation_to_language_candidate_ids: pl.Series = field(init=False)
    ...
        self.citation_to_language_candidate_ids = self.citation_to_language_candidates[
            "document_id"
        ]
