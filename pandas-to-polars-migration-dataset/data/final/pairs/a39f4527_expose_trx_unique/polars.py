import polars as pl

        new_trx_types = trx_data['trx_type'].unique().to_list()
        existing_trx_types = self.trx_types
        conflict_trx_types = set(
            new_trx_types).intersection(existing_trx_types)

        trx_data = (trx_data.
                    lazy().
                    join(date_lookup, how='inner', on='pol_num').
                    filter(pl.col('trx_date') >= pl.col(date_cols[0]),
                           pl.col('trx_date') <= pl.col(date_cols[1])).
                    with_columns(
                        trx_n=1
                    ).collect())

        trx_data = (trx_data.
                    pivot(values=['trx_n', 'trx_amt'],
                          index=['pol_num', date_cols[0]],
                          columns='trx_type',
                          aggregate_function='sum').
                    lazy())

        self.data = (self.data.lazy().
                     join(trx_data,
                          on=['pol_num', date_cols[0]],
                          how='left').
                     with_columns(cs.matches("^trx_(n|amt)_").fill_null(0)).
                     collect())
