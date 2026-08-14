import pandas as pd

        return pd.DataFrame(
            results, columns=["pro_ac", "tx_ac", "alt_ac", "cds_start_i"]
        ).drop_duplicates()
