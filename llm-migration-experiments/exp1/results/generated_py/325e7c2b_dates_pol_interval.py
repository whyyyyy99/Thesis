import numpy as np
import polars as pl
from dateutil.relativedelta import relativedelta

def pol_interval(dates: str | datetime | DatetimeIndex | pd.Series,
                 issue_date: str | datetime | DatetimeIndex | pd.Series,
                 dur_length: str) -> np.ndarray:
    arg_match('dur_length', dur_length, ['year', 'quarter', 'month', 'week'])

    dates = _convert_date(dates)
    issue_date = _convert_date(issue_date)

    def _to_list(x):
        if isinstance(x, (str, bytes)):
            return [x]
        try:
            return list(x)
        except TypeError:
            return [x]

    dates_list = _to_list(dates)
    issue_date_list = _to_list(issue_date)
    n = max(len2(dates), len2(issue_date))

    if len(dates_list) < n:
        dates_list = dates_list + [None] * (n - len(dates_list))
    if len(issue_date_list) < n:
        issue_date_list = issue_date_list + [None] * (n - len(issue_date_list))

    dat = pl.DataFrame({
        'issue_date': issue_date_list,
        'dates': dates_list
    })

    if dur_length == "year":
        res = [relativedelta(a, b).years for a, b in
               zip(dat.get_column("dates"), dat.get_column("issue_date"))]

    elif dur_length in ["month", "quarter"]:
        def mth_calc(a, b):
            delta = relativedelta(a, b)
            return 12 * delta.years + delta.months

        if dur_length == "quarter":
            res = [mth_calc(a, b) // 3 for a, b in
                   zip(dat.get_column("dates"), dat.get_column("issue_date"))]
        else:
            res = [mth_calc(a, b) for a, b in zip(dat.get_column("dates"), dat.get_column("issue_date"))]

    else:
        res = (dat.get_column("dates") - dat.get_column("issue_date")).dt.days // 7

    return np.array(res) + 1
