    query_frame = pl.DataFrame(dict(query_d3_document_id=documents_frame["d3_document_id"]))
    candidate_frame = pl.DataFrame(dict(candidate_d3_document_id=documents_frame["d3_document_id"]))
    return query_frame.join(candidate_frame, how="cross")
