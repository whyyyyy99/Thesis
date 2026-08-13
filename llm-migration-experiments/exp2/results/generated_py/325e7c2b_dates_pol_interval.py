import numpy as np
import pandas as pd
import polars as pl
from dateutil.relativedelta import relativedelta
from pandas.core.indexes.datetimes import DatetimeIndex

def pol_interval(dates: str | datetime | DatetimeIndex | pd.Series,
                 issue_date: str | datetime | DatetimeIndex | pd.Series,
                 dur_length: str) -> np.ndarray:
    arg_match('dur_length', dur_length, ['year', 'quarter', 'month', 'week'])

    dates = _convert_date(dates)
    issue_date = _convert_date(issue_date)

    n = max(len2(dates), len2(issue_date))

    def _to_list(x, n):
        if isinstance(x, pl.Series):
            vals = x.to_list()
        elif isinstance(x, (pd.Series, DatetimeIndex, np.ndarray, list, tuple)):
            vals = list(x)
        else:
            return [x] * n
        if len(vals) < n:
            vals = vals + [None] * (n - len(vals))
        return vals

    dates = _to_list(dates, n)
    issue_date = _to_list(issue_date, n)

    dat = pl.DataFrame({
        'issue_date': issue_date,
        'dates': dates
    })

    if dur_length == "year":
        res = [relativedelta(a, b).years for a, b in
               zip(dat["dates"].to_list(), dat["issue_date"].to_list())]

    elif dur_length in ["month", "quarter"]:
        def mth_calc(a, b):
            delta = relativedelta(a, b)
            return 12 * delta.years + delta.months

        if dur_length == "quarter":
            res = [mth_calc(a, b) // 3 for a, b
                   in zip(dat["dates"].to_list(), dat["issue_date"].to_list())]
        else:
            res = [mth_calc(a, b) for a, b in zip(dat["dates"].to_list(), dat["issue_date"].to_list())]

    else:
        res = (pl.Series(dat["dates"]) - pl.Series(dat["issue_date"])).dt.total_days().to_list()
        res = [x // 7 if x is not None else None for x in res]

    return np.array(res) + 1