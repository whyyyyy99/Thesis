        self.df = self.df.with_columns(
            [
                pl.col("Low").rolling_min(window_size=window).alias("low_min"),
                pl.col("High").rolling_max(window_size=window).alias("high_max"),
            ]
        )
        self.df = self.df.with_columns(
            [
                (
                    (pl.col("Close") - pl.col("low_min"))
                    / (pl.col("high_max") - pl.col("low_min"))
                    * 100
                ).alias("stoch")
            ]
        )
        self.df = self.df.with_columns(
            [pl.col("stoch").rolling_mean(window_size=smooth_window).alias("stoch_signal")]
        )
        self.df = self.df.drop(["low_min", "high_max"])
