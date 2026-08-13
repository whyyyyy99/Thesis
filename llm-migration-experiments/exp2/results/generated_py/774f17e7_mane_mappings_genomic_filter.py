mane_rows = self.df.filter(
    (pl.lit(start) >= pl.col("chr_start").cast(pl.Int64))
    & (pl.lit(end) <= pl.col("chr_end").cast(pl.Int64))
    & (pl.col("GRCh38_chr") == alt_ac)
).sort("MANE_status", descending=False)
return mane_rows.to_dicts()