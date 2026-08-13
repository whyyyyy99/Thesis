import os
import polars as pl

return pl.read_csv(
    os.path.dirname(__file__).replace("utils", "resources/hgnc_complete_set.txt"),
    separator="\t",
    schema_overrides=str,
)
