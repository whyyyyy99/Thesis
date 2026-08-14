import pandas as pd

        copy_df["ac_no_version_as_int"] = copy_df["tx_ac"].apply(
            lambda x: int(x.split(".")[0].split("NM_")[1])
        )
        copy_df["ac_version"] = copy_df["tx_ac"].apply(lambda x: x.split(".")[1])
        copy_df = copy_df.sort_values(
            ["ac_no_version_as_int", "ac_version"], ascending=[False, False]
        )
