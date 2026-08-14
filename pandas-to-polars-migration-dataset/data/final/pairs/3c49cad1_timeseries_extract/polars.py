        param_data.values = param_data.values.with_columns(
            pl.lit(result_series_param).alias(f"S{result_series_param.name}")
        )
