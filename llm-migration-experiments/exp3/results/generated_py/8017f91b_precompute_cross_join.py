import polars as pl

return (
    pl.DataFrame({"document_id": pl.Series("document_id", range(input_df.height))})
    .with_columns(
        pl.col("document_id").map_elements(
            lambda query_d3_document_id: find_top_n_matches_single_document(
                input_df, query_d3_document_id, pairwise_metric, n
            )
        ).alias("scores")
    )
)
