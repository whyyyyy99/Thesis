import pandas as pd

    a = df[df["condition"] == condition_a][metric].to_numpy()
    b = df[df["condition"] == condition_b][metric].to_numpy()
