import polars as pl

data = data.rename(
    {
        col_pol_num: "pol_num",
        col_status: "status",
        col_exposure: "exposure",
    },
    strict=False,
)

if not cal_expo and col_pol_per is not None:
    data = data.rename({col_pol_per: exp_col_pol_per}, strict=False)

if cols_dates is not None:
    data = data.rename(
        {
            cols_dates[0]: exp_cols_dates[0],
            cols_dates[1]: exp_cols_dates[1],
        },
        strict=False,
    )

if trx_types is not None:
    data = data.rename(trx_renamer)