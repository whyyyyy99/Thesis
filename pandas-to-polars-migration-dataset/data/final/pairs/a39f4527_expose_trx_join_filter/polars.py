                    lazy().
                    join(date_lookup, how='inner', on='pol_num').
                    filter(pl.col('trx_date') >= pl.col(date_cols[0]),
                           pl.col('trx_date') <= pl.col(date_cols[1])).
                    with_columns(
                        trx_n=1
                    ).collect())
