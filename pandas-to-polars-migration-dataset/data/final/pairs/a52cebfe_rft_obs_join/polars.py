                responses = ensemble.load_responses(response_key, tuple(realizations))
                joined = obs_df.join(
                    responses,
                    on=["response_key", "report_step", "index"],
                    how="left",
                ).drop("index", "report_step")
                all_realization_frames = joined.rename(
                    {"realization": "Realization", "values": "Pressure",
                     "observations": "ObsValue", "std": "ObsStd"}
                ).with_columns(
                    [
                        polars.lit(well_key).alias("Well").cast(polars.String),
                        polars.lit(ensemble.name).alias("Ensemble").cast(polars.String),
                        polars.lit(ensemble.iteration).alias("Iteration").cast(polars.UInt8),
                        polars.lit(tvd_arg).alias("TVD").cast(polars.Float32),
                    ]
                )
                data.append(all_realization_frames)
