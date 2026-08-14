def process_edges_dataframe(
    edges: PandasEdgeDataFrameInput,
) -> PolarsEdgeDataFrameInput:
    edges_polars = pl.from_pandas(edges[0])
    return edges_polars, edges[1], edges[2]
