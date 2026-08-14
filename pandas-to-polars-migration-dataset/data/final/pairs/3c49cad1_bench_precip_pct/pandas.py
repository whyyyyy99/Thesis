import pandas as pd

    total_amount = len(df["value"])
    zero_amount = len(df[df["value"] == 0.0])
