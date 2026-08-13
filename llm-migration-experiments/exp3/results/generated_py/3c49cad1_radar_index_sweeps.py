import polars as pl

if not all(files_server["filename"].str.ends_with(".bz2")):
    files_server = files_server.filter(~pl.col("filename").str.ends_with(".bz2"))
