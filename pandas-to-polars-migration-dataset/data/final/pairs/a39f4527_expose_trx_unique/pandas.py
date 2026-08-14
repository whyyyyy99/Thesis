import pandas as pd
import numpy as np

        new_trx_types = pd.unique(trx_data.trx_type)
        existing_trx_types = self.trx_types
        conflict_trx_types = np.intersect1d(new_trx_types, existing_trx_types)

        trx_data = (trx_data
                    .merge(date_lookup, how='inner', on='pol_num')
                    .query(f"(trx_date >= {date_cols[0]}) & (trx_date <= {date_cols[1]})"))

        trx_data['trx_n'] = 1
        trx_data = (trx_data
                    .pivot_table(values=['trx_n', 'trx_amt'],
                                 index=['pol_num', date_cols[0]],
                                 columns='trx_type',
                                 aggfunc='sum',
                                 observed=True,
                                 fill_value=0)
                    .reset_index())

        cols = trx_data.columns.to_flat_index()
        cols = ['_'.join(x) if x[1] != '' else x[0] for x in cols]
        trx_data.columns = cols

        self.data = self.data.merge(trx_data, on=['pol_num', date_cols[0]], how='left')
        self.data.loc[:, trx_cols] = self.data.loc[:, trx_cols].apply(lambda x: x.fillna(0))
