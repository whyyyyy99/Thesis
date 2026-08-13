import polars as pl

mane_rows = self.df.filter(
    (start >= self.df["chr_start"].cast(pl.Int64))
    & (end <= self.df["chr_end"].cast(pl.Int64))
    & (self.df["GRCh38_chr"] == alt_ac)
)
mane_rows = mane_rows.sort("MANE_status", descending=True)
return mane_rows.to_dicts()
