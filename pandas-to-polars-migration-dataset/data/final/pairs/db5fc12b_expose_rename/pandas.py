import pandas as pd

        data = data.rename(columns={
            col_pol_num: 'pol_num',
            col_status: 'status',
            col_exposure: 'exposure'
        })

        if not cal_expo and col_pol_per is not None:
            data = data.rename(columns={col_pol_per: exp_col_pol_per})

        if cols_dates is not None:
            data = data.rename(columns={
                cols_dates[0]: exp_cols_dates[0],
                cols_dates[1]: exp_cols_dates[1]
            })

        if trx_types is not None:
            data.columns = [trx_renamer(x) for x in data.columns]
