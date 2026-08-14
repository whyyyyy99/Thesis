    if not df_fileindex.get_column("filename").str.ends_with(".bz2").all():
        df_fileindex = df_fileindex.filter(~pl.col("filename").str.ends_with(".bz2"))
