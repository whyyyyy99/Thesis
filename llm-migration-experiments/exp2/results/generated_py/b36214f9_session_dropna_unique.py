import polars as pl

unique_values = database_info["db"].drop_nulls().unique(maintain_order=True)