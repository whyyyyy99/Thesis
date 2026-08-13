import polars as pl

content_df = pl.concat([pl.DataFrame(item) for item in content])