import polars as pl

rft_data = pl.DataFrame(pressure_vals)
ensemble_data = []
for iens in realizations:
    frame = pl.DataFrame(
        data={
            "TVD": tvd_arg,
            "Pressure": rft_data.get_column(iens),
            "ObsValue": obs_node["observations"].to_numpy()[0],
            "ObsStd": obs_node["std"].to_numpy()[0],
        },
    )
    frame = frame.with_columns(
        pl.lit(iens).alias("Realization"),
        pl.lit(well).alias("Well"),
    )
    ensemble_data.append(frame)
data.append(pl.concat(ensemble_data))
