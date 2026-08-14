import pandas as pd

def to_frame(self) -> pd.DataFrame:
    """Collect all scores in a DataFrame."""
    return pd.DataFrame(
        {
            "Language Model": self.language_model_name,
            "Citation -> Language Candidates": round(
                self.citation_to_language_candidates, ndigits=3
            ),
            "Citation -> Language Final": round(self.citation_to_language, ndigits=3),
            "Language -> Citation Candidates": round(
                self.language_to_citation_candidates, ndigits=3
            ),
            "Language -> Citation Final": round(self.language_to_citation, ndigits=3),
        },
        index=[0],
    )
