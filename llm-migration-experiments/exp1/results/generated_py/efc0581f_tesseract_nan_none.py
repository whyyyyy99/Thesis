import numpy as np
import polars as pl

d_el = d_el.with_columns(pl.lit(np.nan).alias("confidence"))
