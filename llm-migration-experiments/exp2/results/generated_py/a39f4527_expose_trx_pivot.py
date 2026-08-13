import polars as pl

trx_data = (
    trx_data.pivot(
        values=['trx_n', 'trx_amt'],
        index=['pol_num', date_cols[0]],
        columns='trx_type',
        aggregate_function='sum',
        fill_value=0,
        maintain_order=True,
        sort_columns=False,
        separator='_',
    )
)
# flatten column index
cols = trx_data.columns
cols = ['_'.join(x) if isinstance(x, tuple) and len(x) > 1 and x[1] != '' else (x[0] if isinstance(x, tuple) else x) for x in cols]
trx_data.columns = cols