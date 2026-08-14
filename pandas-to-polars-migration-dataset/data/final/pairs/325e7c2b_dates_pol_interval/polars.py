import polars as pl

def pol_interval(dates: str | date | list | pl.Series,
                 issue_date:  str | date | list | pl.Series,
                 dur_length: str) -> pl.Series:
    arg_match('dur_length', dur_length, ['year', 'quarter', 'month', 'week'])

    dates = _convert_date(dates)
    issue_date = _convert_date(issue_date)

    if dur_length == 'year':
        interval = '1y'
    elif dur_length == 'quarter':
        interval = '1q'
    elif dur_length == 'month':
        interval = '1mo'
    else:
        interval = '1w'

    return pl.date_ranges(issue_date, dates, interval, eager=True).list.len()
