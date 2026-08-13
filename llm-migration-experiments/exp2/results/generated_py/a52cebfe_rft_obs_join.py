import polars as pl

rft_data = pl.DataFrame(pressure_vals)
ensemble_data = []
for iens in realizations:
    realization_frame = pl.DataFrame(
        {
            "TVD": tvd_arg,
            "Pressure": rft_data.get_column(iens),
            "ObsValue": obs_node["observations"].to_list()[0],
            "ObsStd": obs_node["std"].to_list()[0],
        }
    )
    realization_frame = realization_frame.with_columns(
        pl.lit(iens).alias("Realization"),
        pl.lit(well).alias("Well"),
    )
    ensemble_data.append(realization_frame)
data.append(pl.concat(ensemble_data))