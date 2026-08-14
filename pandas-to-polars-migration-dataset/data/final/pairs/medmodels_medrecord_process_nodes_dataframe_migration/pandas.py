import pandas as pd

def process_nodes_dataframe(nodes: pd.DataFrame) -> PolarsNodeDataFrameInput:
    assert isinstance(nodes.index, pd.Index), "Nodes dataframe must have an Index"
    assert nodes.index.name is not None, "Nodes dataframe must have an Index"
    nodes_polars = pl.from_pandas(nodes, include_index=True)
    return nodes_polars, nodes.index.name
