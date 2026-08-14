import pandas as pd

average_precision_scores = pd.concat(frames)
    return (
        average_precision_scores
        .sort_values("Best Score", ascending=False)
        .reset_index(drop=False)
        .drop_duplicates(subset="Query Document ID")
        .reset_index(drop=True)
    )
