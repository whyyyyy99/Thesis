import polars as pl

trx_data = trx_data.pivot(
    index=["pol_num", date_cols[0]],
    columns="trx_type",
    values=["trx_n", "trx_amt"],
    aggregate_function="sum",
    sort_columns=True,
)
trx_data = trx_data.with_columns(pl.exclude(["pol_num", date_cols[0]]).fill_null(0))
