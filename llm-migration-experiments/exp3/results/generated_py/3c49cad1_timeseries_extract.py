param_data.values = param_data.values.with_columns(pl.Series(f"S{result_series_param.name}", result_series_param.values))
