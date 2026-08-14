import pandas as pd

    return (
        pd.DataFrame(data=input_df.index, columns=["document_id"])
        .assign(
            scores=lambda new_df: new_df["document_id"].progress_apply(
                lambda query_d3_document_id: find_top_n_matches_single_document(
                    input_df, query_d3_document_id, pairwise_metric, n
                )
            )
        )
        .set_index("document_id")
    )
