            pivoted = responses_for_type.pivot(
                on="realization",
                index=["response_key", *response_cls.primary_key],
                aggregate_function="mean",
            )
            if "time" in pivoted:
                joined = observations_for_type.join_asof(pivoted, ...)
            else:
                joined = observations_for_type.join(pivoted, how="left", ...)
            dfs.append(joined)
        df = polars.concat(dfs)
        df = df.rename({"observations": "OBS", "std": "STD"})
        pddf = df.to_pandas()[[...]]
        pddf = pddf.set_index(["observation_key", "key_index"]).transpose()
        return pddf
