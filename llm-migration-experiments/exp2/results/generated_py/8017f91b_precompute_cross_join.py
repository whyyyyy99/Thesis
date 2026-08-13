import polars as pl

return (
    pl.DataFrame({"document_id": list(input_df.index)})
    .with_columns(
        pl.col("document_id").map_elements(
            lambda query_d3_document_id: find_top_n_matches_single_document(
                input_df, query_d3_document_id, pairwise_metric, n
            ),
            return_dtype=pl.Object,
        ).alias("scores")
    )
)