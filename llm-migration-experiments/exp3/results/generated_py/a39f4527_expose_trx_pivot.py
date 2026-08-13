trx_data = (
    trx_data.pivot(
        index=["pol_num", date_cols[0]],
        columns="trx_type",
        values=["trx_n", "trx_amt"],
        aggregate_function="sum",
        separator="_",
        maintain_order=True,
    )
    .fill_null(0)
    .reset_index()
)
cols = trx_data.columns
trx_data.columns = cols
