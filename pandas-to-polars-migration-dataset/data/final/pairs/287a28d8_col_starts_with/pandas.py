import pandas as pd

def col_starts_with(data: pd.DataFrame,
                    pat: str,
                    **kwargs):
    return list(data.columns[data.columns.str.startswith(pat, **kwargs)])
