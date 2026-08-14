import pandas as pd

    language_to_citation_candidate_ids: pd.Index = field(init=False)
    ...
        self.language_to_citation_candidate_ids = self.language_to_citation_candidates.index
