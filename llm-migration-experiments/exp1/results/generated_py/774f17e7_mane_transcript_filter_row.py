import polars as pl

if df.is_empty():
    logger.warning(f"Unable to get transcripts from gene {gene}")
    return None

for tx_ac in prioritized_tx_acs:
    tmp_df = df.filter(pl.col("tx_ac") == tx_ac).sort("alt_ac", descending=True)
    row = tmp_df.to_dicts()[0]
