import pandas as pd

        if df.empty:
            logger.warning(f"Unable to get transcripts from gene {gene}")
            return None

        for tx_ac in prioritized_tx_acs:
            tmp_df = df.loc[df["tx_ac"] == tx_ac].sort_values("alt_ac", ascending=False)
            row = tmp_df.iloc[0]
