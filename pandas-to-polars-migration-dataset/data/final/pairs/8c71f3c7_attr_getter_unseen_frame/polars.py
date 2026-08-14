        return pl.DataFrame(
            {
                "document_id": [-1],
                "scores": [sort_document_scores(common_citations_scores)],
            }
        )
