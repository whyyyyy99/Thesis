import pandas as pd
from pandas.core.indexes.datetimes import DatetimeIndex

def pol_interval(dates: str | datetime | DatetimeIndex | pd.Series,
                 issue_date: str | datetime | DatetimeIndex | pd.Series,
                 dur_length: str) -> np.ndarray:
    arg_match('dur_length', dur_length, ['year', 'quarter', 'month', 'week'])

    dates = _convert_date(dates)
    issue_date = _convert_date(issue_date)

    dat = pd.DataFrame({
        'issue_date': issue_date,
        'dates': dates
    }, index=np.arange(max(len2(dates), len2(issue_date))))

    if dur_length == "year":
        res = [relativedelta(a, b).years for a, b in
               zip(dat.dates, dat.issue_date)]

    elif dur_length in ["month", "quarter"]:
        def mth_calc(a, b):
            delta = relativedelta(a, b)
            return 12 * delta.years + delta.months

        if dur_length == "quarter":
            res = [mth_calc(a, b) // 3 for a, b
                   in zip(dat.dates, dat.issue_date)]
        else:
            res = [mth_calc(a, b) for a, b in zip(dat.dates, dat.issue_date)]

    else:
        res = (dat.dates - dat.issue_date).dt.days // 7

    return np.array(res) + 1
