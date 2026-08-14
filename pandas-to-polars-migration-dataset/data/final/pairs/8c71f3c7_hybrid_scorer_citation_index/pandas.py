import pandas as pd

    citation_to_language_candidate_ids: pd.Index = field(init=False)
    ...
        self.citation_to_language_candidate_ids = self.citation_to_language_candidates.index
