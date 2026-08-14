        mane_rows = self.df.filter(
            (start >= pl.col("chr_start"))
            & (end <= pl.col("chr_end"))
            & (pl.col("GRCh38_chr") == alt_ac)
        )
        mane_rows = mane_rows.sort(by="MANE_status", descending=True)
        return mane_rows.to_dicts()
