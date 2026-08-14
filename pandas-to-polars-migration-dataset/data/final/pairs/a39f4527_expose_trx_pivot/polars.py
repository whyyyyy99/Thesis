                    pivot(values=['trx_n', 'trx_amt'],
                          index=['pol_num', date_cols[0]],
                          columns='trx_type',
                          aggregate_function='sum').
                    lazy())
