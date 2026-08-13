import polars as pl

df_chunk = load_df_from_pickle(filepath)
df_combined = pl.concat(df_list)
write_df_to_pickle(df_combined, path_documents_labels)
