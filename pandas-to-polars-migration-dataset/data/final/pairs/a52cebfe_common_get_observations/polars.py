    for response_type, df in experiment.observations.items():
        if observation_keys is not None:
            df = df.filter(polars.col("observation_key").is_in(observation_keys))
        if df.is_empty():
            continue
        df = df.rename({"observation_key": "name", "std": "errors", "observations": "values"})
        df = df.with_columns(polars.Series(name="x_axis", values=df.map_rows(x_axis_fn)))
        df = df.sort("x_axis")
        for obs_key, _obs_df in df.group_by("name"):
            observations.append({
                "name": obs_key[0],
                "values": _obs_df["values"].to_list(),
                "errors": _obs_df["errors"].to_list(),
                "x_axis": _obs_df["x_axis"].to_list(),
            })
