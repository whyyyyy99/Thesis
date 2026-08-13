import pandas as pd
import polars as pl

pl.Series([pd.Timestamp(i.text) for i in timesteps.getchildren()])
