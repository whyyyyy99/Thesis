import polars as pl
from dataclasses import field

    citation_to_language_candidate_ids: pl.Series = field(init=False)
    ...
        self.citation_to_language_candidate_ids = (
            self.citation_to_language_candidates.get_column("index")
            if "index" in self.citation_to_language_candidates.columns
            else pl.Series(name="citation_to_language_candidate_ids", values=[])
        )
