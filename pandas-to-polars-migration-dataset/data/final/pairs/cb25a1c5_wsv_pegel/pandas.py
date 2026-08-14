import pandas as pd

        df = pd.read_json(response)
        df = pl.from_pandas(df).lazy()
