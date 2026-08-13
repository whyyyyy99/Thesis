import polars as pl
from typing import cast

return cast(
    str,
    self.documents_data.filter(pl.col("d3_document_id") == d3_document_id)
    .select("semanticscholar_url")
    .item(),
)
