if not files_server["filename"].str.ends_with(".bz2").all():
    files_server = files_server.filter(~pl.col("filename").str.ends_with(".bz2"))