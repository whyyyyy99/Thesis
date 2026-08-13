import pandas as pd
import polars as pl


def col_starts_with(data: pl.DataFrame,
                    pat: str,
                    **kwargs):
    try:
        return list(data.columns[[c.startswith(pat, **kwargs) for c in data.columns]])
    except TypeError:
        return list(data.columns[[c.startswith(pat) for c in data.columns]])
