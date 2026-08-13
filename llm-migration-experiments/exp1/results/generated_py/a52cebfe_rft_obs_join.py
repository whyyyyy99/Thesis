import polars as pl

rft_data = pl.DataFrame(pressure_vals)
ensemble_data = []
for iens in realizations:
    frame = pl.DataFrame(
        {
            "TVD": tvd_arg,
            "Pressure": rft_data.get_column(iens),
            "ObsValue": [obs_node["observations"].values[0]] * len(tvd_arg),
            "ObsStd": [obs_node["std"].values[0]] * len(tvd_arg),
        }
    )
    frame = frame.with_columns(
        [
            pl.lit(iens).alias("Realization"),
            pl.lit(well).alias("Well"),
        ]
    )
    ensemble_data.append(frame)
data.append(pl.concat(ensemble_data))
