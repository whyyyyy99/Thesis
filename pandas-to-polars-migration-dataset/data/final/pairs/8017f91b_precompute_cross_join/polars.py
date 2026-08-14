    id_combinations_frame = generate_id_combinations_frame(documents_frame).pipe(
        remove_matching_id_rows
    )
    scores_frame = pairwise_scores_from_columns(
        documents_frame, id_combinations_frame, pairwise_metric
    ).sort(by=["query_d3_document_id", "score"], descending=[False, True])
    return scores_frame.groupby("query_d3_document_id").head(n)
