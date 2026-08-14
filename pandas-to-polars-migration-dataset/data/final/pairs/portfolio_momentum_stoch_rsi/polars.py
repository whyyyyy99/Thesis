        self.df = self.df.with_columns(
            [
                pl.col("RSI").rolling_min(window_size=window).alias("rsi_min"),
                pl.col("RSI").rolling_max(window_size=window).alias("rsi_max"),
            ]
        )
        self.df = self.df.with_columns(
            [
                (
                    (pl.col("RSI") - pl.col("rsi_min"))
                    / (pl.col("rsi_max") - pl.col("rsi_min"))
                    * 100
                ).alias("stoch_rsi_k")
            ]
        )
        self.df = self.df.with_columns(
            [pl.col("stoch_rsi_k").rolling_mean(window_size=smooth1).alias("stoch_rsi_d")]
        )
        self.df = self.df.with_columns([pl.col("stoch_rsi_d").alias("stoch_rsi")])
        self.df = self.df.drop(["rsi_min", "rsi_max"])
