import math
import polars as pl

row_indices.append(
    lookup.filter(pl.col("uid") == id_).select("row_index").to_series()[0]
)
column_indices.append(
    lookup.filter(pl.col("uid") == id_).select("column_index").to_series()[0]
)
row_indices = [i for i in row_indices if i is not None and not (isinstance(i, float) and math.isnan(i))]
column_indices = [i for i in column_indices if i is not None and not (isinstance(i, float) and math.isnan(i))]