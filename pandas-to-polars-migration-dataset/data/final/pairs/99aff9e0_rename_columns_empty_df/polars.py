        # Convert to polars while preserving dtypes, then create empty DataFrame with correct schema
        polars_df = pl.from_pandas(df)
        df = pl.DataFrame(schema=polars_df.schema)
