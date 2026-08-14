import pandas as pd

                    pivot_table(values=['trx_n', 'trx_amt'],
                                index=['pol_num', date_cols[0]],
                                columns='trx_type',
                                aggfunc='sum',
                                observed=True,
                                fill_value=0).
                    reset_index())
        # flatten column index
        cols = trx_data.columns.to_flat_index()
        cols = ['_'.join(x) if x[1] != '' else x[0] for x in cols]
        trx_data.columns = cols
