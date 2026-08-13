import pandas as pd
import polars as pl

def process_edges_dataframe(edges: pd.DataFrame) -> PolarsEdgeDataFrameInput:
    assert isinstance(
        edges.index, pd.MultiIndex
    ), "Edges dataframe must have a MultiIndex"
    assert len(edges.index.names) == 2, "Edges dataframe MultiIndex must have 2 levels"
    edges_polars = pl.from_pandas(edges, include_index=True)
    return edges_polars, edges.index.names[0], edges.index.names[1]
