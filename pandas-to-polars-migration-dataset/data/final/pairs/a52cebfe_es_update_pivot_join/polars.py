        pivoted = responses_for_type.pivot(
            on="realization",
            index=["response_key", *response_cls.primary_key],
            aggregate_function="mean",
        )
        if "time" in pivoted:
            joined = observations_for_type.join_asof(
                pivoted,
                by=["response_key", *response_cls.primary_key],
                on="time",
            )
        else:
            joined = observations_for_type.join(
                pivoted, how="left", on=["response_key", *response_cls.primary_key],
            )
        obs_keys_1d = joined["observation_key"].to_numpy()
        obs_values_1d = joined["observations"].to_numpy()
        obs_errors_1d = joined["std"].to_numpy()
        responses = joined.select(joined.columns[num_non_response_value_columns:]).to_numpy()
        filtered_responses.append(responses)
        observation_keys.append(obs_keys_1d)
        observation_values.append(obs_values_1d)
        observation_errors.append(obs_errors_1d)
        indexes.append(index_1d)
