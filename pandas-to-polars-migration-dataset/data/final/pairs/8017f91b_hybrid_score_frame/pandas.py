import pandas as pd

def to_frame(language_model_name, citation_to_language_candidates, citation_to_language, language_to_citation_candidates, language_to_citation):
    return pd.DataFrame(
        {
            "Language Model": language_model_name,
            "Citation -> Language Candidates": round(
                citation_to_language_candidates, ndigits=3
            ),
            "Citation -> Language Final": round(citation_to_language, ndigits=3),
            "Language -> Citation Candidates": round(
                language_to_citation_candidates, ndigits=3
            ),
            "Language -> Citation Final": round(language_to_citation, ndigits=3),
        },
        index=[0],
    )
