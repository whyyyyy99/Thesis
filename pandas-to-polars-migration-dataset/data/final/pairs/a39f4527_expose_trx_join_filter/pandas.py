import pandas as pd

                    merge(date_lookup, how='inner', on='pol_num').
                    query(f"(trx_date >= {date_cols[0]}) & " +
                          f"(trx_date <= {date_cols[1]})"))
        trx_data['trx_n'] = 1
