df_words = (ocr_df.df.filter(pl.col('class') == "ocrx_word")
                .filter(pl.col('confidence') >= 50)
                )
