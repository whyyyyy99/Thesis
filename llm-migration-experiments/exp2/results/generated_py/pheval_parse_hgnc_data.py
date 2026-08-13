import os
import polars as pl

return pl.read_csv(
    os.path.dirname(__file__).replace("utils", "resources/hgnc_complete_set.txt"),
    separator="\t",
).select(pl.all().cast(pl.Utf8))