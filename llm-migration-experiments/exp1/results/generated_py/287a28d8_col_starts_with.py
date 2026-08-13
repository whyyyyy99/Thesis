import polars as pl

def col_starts_with(data: pl.DataFrame,
                    pat: str,
                    **kwargs):
    return [col for col in data.columns if col.startswith(pat, **kwargs)]
