import polars as pl

def col_starts_with(data: pl.DataFrame,
                    pat: str,
                    **kwargs):
    return list([c for c in data.columns if c.startswith(pat, **kwargs)])