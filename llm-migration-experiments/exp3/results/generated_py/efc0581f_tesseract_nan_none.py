import polars as pl

d_el = d_el.with_columns(pl.lit(float("nan")).alias("confidence"))
