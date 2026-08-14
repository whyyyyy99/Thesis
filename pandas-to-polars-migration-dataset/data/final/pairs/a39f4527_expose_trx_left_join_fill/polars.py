        self.data = (self.data.lazy().
                     join(trx_data,
                          on=['pol_num', date_cols[0]],
                          how='left').
                     with_columns(cs.matches("^trx_(n|amt)_").fill_null(0)).
                     collect())
