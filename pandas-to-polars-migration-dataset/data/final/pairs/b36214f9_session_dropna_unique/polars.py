        unique_values = (
            database_info.get_column("db")
            .drop_nulls()
            .unique()
            .to_list()
        )
        unique_values = [v for v in unique_values if v and str(v).strip()]
