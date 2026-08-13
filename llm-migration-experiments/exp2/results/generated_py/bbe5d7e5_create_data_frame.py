import numpy as np
import polars as pl

toy_census = pl.DataFrame({
    'pol_num': np.arange(1, 4),
    'status': pl.Series(["Active", "Death", "Surrender"], dtype=pl.Categorical),
    'issue_date': pl.Series(pl.Series(["2010-01-01", "2011-05-27", "2009-11-10"]).str.to_datetime()),
    'term_date': pl.Series([None, "2020-09-14", "2022-02-25"]).str.to_datetime(),
})