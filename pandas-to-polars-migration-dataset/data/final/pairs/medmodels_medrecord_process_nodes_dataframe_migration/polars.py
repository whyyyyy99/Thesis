def process_nodes_dataframe(
    nodes: PandasNodeDataFrameInput,
) -> PolarsNodeDataFrameInput:
    nodes_polars = pl.from_pandas(nodes[0])
    return nodes_polars, nodes[1]
