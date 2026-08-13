import polars as pl

return OCRDataframe(df=self.df.filter(pl.col("page") == page_number))
