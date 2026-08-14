    filtered_df = df.filter(pl.col("date").eq(day_time))
    values = filtered_df.get_column("value").to_list()
