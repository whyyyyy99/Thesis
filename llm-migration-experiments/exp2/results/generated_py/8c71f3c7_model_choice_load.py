import pandas as pd
import polars as pl

return pl.from_pandas(load_df_from_pickle(cosine_similarities_path))