import polars as pl

df_words = ocr_df.df.filter(pl.col("class") == "ocrx_word")
df_words = df_words.filter((pl.col("confidence") >= 50) | pl.col("confidence").is_null())