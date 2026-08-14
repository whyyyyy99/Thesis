import pandas as pd

        df = pd.read_csv(response)
        return df.rename(
            columns={GEOSPHERE_RENAME_MAP}
        ).drop(columns=["Sonnenschein", "Globalstrahlung"])
