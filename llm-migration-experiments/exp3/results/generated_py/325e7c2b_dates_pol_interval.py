import numpy as np
import pandas as pd
import polars as pl
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas.core.indexes.datetimes import DatetimeIndex


def arg_match(name, value, allowed):
    if value not in allowed:
        raise ValueError(f"{name} must be one of {allowed!r}")


def len2(x):
    if isinstance(x, (pd.Series, DatetimeIndex, pl.Series, list, tuple, np.ndarray)):
        return len(x)
    return 1


def _convert_date(x):
    if isinstance(x, (pd.Series, DatetimeIndex)):
        return pd.to_datetime(x).to_pydatetime().tolist()
    if isinstance(x, pl.Series):
        return pd.to_datetime(x.to_list()).to_pydatetime().tolist()
    if isinstance(x, np.ndarray):
        return pd.to_datetime(x).to_pydatetime().tolist()
    if isinstance(x, (list, tuple)):
        return pd.to_datetime(list(x)).to_pydatetime().tolist()
    if x is None:
        return [None]
    if isinstance(x, (str, datetime, pd.Timestamp)):
        return [pd.to_datetime(x).to_pydatetime()]
    return [x]


def pol_interval(dates: str | datetime | DatetimeIndex | pd.Series,
                 issue_date: str | datetime | DatetimeIndex | pd.Series,
                 dur_length: str) -> np.ndarray:
    arg_match('dur_length', dur_length, ['year', 'quarter', 'month', 'week'])

    dates = _convert_date(dates)
    issue_date = _convert_date(issue_date)

    n = max(len2(dates), len2(issue_date))
    if len(dates) == 1 and n > 1:
        dates = dates * n
    if len(issue_date) == 1 and n > 1:
        issue_date = issue_date * n

    dat = pl.DataFrame({
        'issue_date': issue_date,
        'dates': dates
    })

    if dur_length == "year":
        res = [relativedelta(a, b).years for a, b in zip(dat["dates"].to_list(), dat["issue_date"].to_list())]

    elif dur_length in ["month", "quarter"]:
        def mth_calc(a, b):
            delta = relativedelta(a, b)
            return 12 * delta.years + delta.months

        if dur_length == "quarter":
            res = [mth_calc(a, b) // 3 for a, b in zip(dat["dates"].to_list(), dat["issue_date"].to_list())]
        else:
            res = [mth_calc(a, b) for a, b in zip(dat["dates"].to_list(), dat["issue_date"].to_list())]

    else:
        res = [(a - b).days // 7 for a, b in zip(dat["dates"].to_list(), dat["issue_date"].to_list())]

    return np.array(res) + 1
