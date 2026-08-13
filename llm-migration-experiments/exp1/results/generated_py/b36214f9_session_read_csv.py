import polars as pl
from io import StringIO

database_info = pl.read_csv(StringIO(query_result))

if database_info.is_empty() or "db" not in database_info.columns:
    logger.warning("No column information found in the RDF store")
    return None

unique_values = database_info["db"].drop_nulls().unique(maintain_order=True)
