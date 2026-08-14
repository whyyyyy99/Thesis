import pandas as pd

        df = summary_data.to_dataframe()
        df = df.xs(key, level="name")
        df.index = df.index.rename(
            {"time": "Date", "realization": "Realization"}
        ).reorder_levels(["Realization", "Date"])
