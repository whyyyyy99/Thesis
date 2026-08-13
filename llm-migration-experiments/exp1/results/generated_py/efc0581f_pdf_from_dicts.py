import polars as pl

content_df = pl.concat([pl.DataFrame(x) for x in content])
