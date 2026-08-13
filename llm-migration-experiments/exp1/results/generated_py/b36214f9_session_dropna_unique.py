import polars as pl

unique_values = database_info["db"].drop_nulls().drop_nans().unique(maintain_order=True).to_numpy()
