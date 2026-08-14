        self.df = self.df.with_columns(
            [
                (
                    (pl.col("Close") - pl.col("Close").shift(window))
                    / pl.col("Close").shift(window)
                    * 100
                ).alias("ROC")
            ]
        )
