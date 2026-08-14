    return pl.read_csv(stream,
                       dtypes={'pol_num': int,
                               'status': pl.Categorical,
                               'issue_date': date,
                               'term_date': date})
