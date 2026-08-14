import pandas as pd

    return pd.read_csv(stream,
                       index_col=0,
                       dtype={'pol_num': int,
                              'status': 'category'},
                       parse_dates=['issue_date', 'term_date'])
