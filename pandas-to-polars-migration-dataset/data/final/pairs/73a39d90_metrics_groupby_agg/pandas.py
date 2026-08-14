import pandas as pd

        summary = (
            df.groupby("condition")[metric]
            .agg(["mean", "median"])
            .rename(columns={"mean": "mean", "median": "median"})
            .astype(float)
        )
        mixed_mean_raw = cast(SupportsFloat, summary.loc["mixed", "mean"])
        plaintext_mean_raw = cast(SupportsFloat, summary.loc["plaintext", "mean"])
        mixed_mean = float(mixed_mean_raw)
        plaintext_mean = float(plaintext_mean_raw)
