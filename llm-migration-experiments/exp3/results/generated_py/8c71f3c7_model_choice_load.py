import polars as pl
import pandas as pd

obj = load_df_from_pickle(cosine_similarities_path)
if isinstance(obj, pd.DataFrame):
    return pl.from_pandas(obj)
return obj
