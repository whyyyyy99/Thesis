import pandas as pd

        mane_rows = self.df[
            (start >= self.df["chr_start"].astype(int))
            & (end <= self.df["chr_end"].astype(int))
            & (self.df["GRCh38_chr"] == alt_ac)
        ]
        mane_rows = mane_rows.sort_values("MANE_status", ascending=False)
        return mane_rows.to_dict("records")
