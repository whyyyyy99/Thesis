import polars as pl

df = pl.DataFrame(y, schema=["Format", "Status❔", "Size (MB)", key, "Inference time (ms/im)", "FPS"])