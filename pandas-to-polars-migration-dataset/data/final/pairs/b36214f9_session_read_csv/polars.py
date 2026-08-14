        database_info = pl.read_csv(
            StringIO(query_result),
            infer_schema_length=0,
            null_values=[],
            try_parse_dates=False,
        )
        ...
        if database_info.is_empty() or "db" not in database_info.columns:
