import pandas as pd

        return pd.DataFrame(
            {"scores": [sort_document_scores(common_citations_scores)]}, index=[-1]
        ).rename_axis("document_id", axis="index")
