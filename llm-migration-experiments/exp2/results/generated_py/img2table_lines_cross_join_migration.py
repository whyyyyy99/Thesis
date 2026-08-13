import polars as pl

df_w_l = df_words.join(df_lines, how="cross")