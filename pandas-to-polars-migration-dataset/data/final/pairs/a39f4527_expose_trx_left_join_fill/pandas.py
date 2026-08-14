import pandas as pd

        self.data = (self.data.
                     merge(trx_data,
                           on=['pol_num', date_cols[0]],
                           how='left'))
        trx_cols = [x for x in self.data.columns if x.startswith('trx_')]
        self.data.loc[:, trx_cols] = \
            self.data.loc[:, trx_cols].apply(lambda x: x.fillna(0))
