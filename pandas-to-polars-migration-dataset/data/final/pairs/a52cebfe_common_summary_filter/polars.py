        df = (
            summary_data.filter(polars.col("response_key").eq(key))
            .rename({"time": "Date", "realization": "Realization"})
            .drop("response_key")
            .to_pandas()
        )
        df = df.set_index(["Date", "Realization"])
