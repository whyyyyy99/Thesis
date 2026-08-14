    language_to_citation_candidate_ids: pl.Series = field(init=False)
    ...
        self.language_to_citation_candidate_ids = self.language_to_citation_candidates[
            "document_id"
        ]
