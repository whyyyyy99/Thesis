import numpy as np
import polars as pl

toy_census = pl.DataFrame({
    "pol_num": np.arange(1, 4),
    "status": pl.Series("status", ["Active", "Death", "Surrender"], dtype=pl.Categorical),
    "issue_date": pl.Series("issue_date", ["2010-01-01", "2011-05-27", "2009-11-10"]).str.to_datetime(),
    "term_date": pl.Series("term_date", [None, "2020-09-14", "2022-02-25"]).str.to_datetime(),
})
