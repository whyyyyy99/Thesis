        self.df = self.df.with_columns([pl.col("Close").diff().alias("price_change")])
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("price_change") > 0).then(pl.col("price_change")).otherwise(0).alias("gains"),
                pl.when(pl.col("price_change") < 0).then(-pl.col("price_change")).otherwise(0).alias("losses"),
            ]
        )
        self.df = self.df.with_columns(
            [
                pl.col("gains").ewm_mean(span=window, min_periods=min_periods).alias("avg_gains"),
                pl.col("losses").ewm_mean(span=window, min_periods=min_periods).alias("avg_losses"),
            ]
        )
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("avg_losses") == 0)
                .then(100.0)
                .otherwise(100.0 - (100.0 / (1.0 + (pl.col("avg_gains") / pl.col("avg_losses")))))
                .alias("RSI")
            ]
        )
        self.df = self.df.drop(["price_change", "gains", "losses", "avg_gains", "avg_losses"])
