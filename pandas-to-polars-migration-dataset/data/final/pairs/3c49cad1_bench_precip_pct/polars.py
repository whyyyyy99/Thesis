    total_amount = df.get_column("value").len()
    zero_amount = df.filter(pl.col("value").eq(0.0)).height
