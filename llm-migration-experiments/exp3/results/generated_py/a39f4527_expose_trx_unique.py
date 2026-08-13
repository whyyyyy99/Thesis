import polars as pl
import numpy as np

new_trx_types = trx_data.get_column("trx_type").unique(maintain_order=True).to_list()
existing_trx_types = self.trx_types
conflict_trx_types = np.intersect1d(new_trx_types, existing_trx_types)

trx_data = (
    trx_data
    .join(date_lookup, on="pol_num", how="inner")
    .filter((pl.col("trx_date") >= pl.col(date_cols[0])) & (pl.col("trx_date") <= pl.col(date_cols[1])))
)

trx_data = trx_data.with_columns(pl.lit(1).alias("trx_n"))
trx_data = (
    trx_data
    .pivot(
        values=["trx_n", "trx_amt"],
        index=["pol_num", date_cols[0]],
        on="trx_type",
        aggregate_function="sum",
    )
)

cols = trx_data.columns
cols = [col if "_" not in col else col for col in cols]
trx_data.columns = cols

self.data = self.data.join(trx_data, on=["pol_num", date_cols[0]], how="left")
self.data = self.data.with_columns([pl.col(col).fill_null(0) for col in trx_cols])
