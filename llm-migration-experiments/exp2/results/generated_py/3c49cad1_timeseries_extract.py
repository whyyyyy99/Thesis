import polars as pl

param_data = param_data.with_columns(pl.Series(f"S{result_series_param.name}", result_series_param.to_list()))