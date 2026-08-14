import pandas as pd

    df_words = ocr_df.df[ocr_df.df['class'] == 'ocrx_word']
    df_words = df_words[(df_words['confidence'] >= 50) | df_words['confidence'].isna()]
