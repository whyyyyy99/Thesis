import pandas as pd

    df = pd.DataFrame({primary_key.name: primary_key, score.name: score}).set_index(
        primary_key.name, drop=True
    )
    df = df.sort_values(by=str(score.name), ascending=ascending)
    df["rank"] = np.ceil(np.arange(1, len(df) + 1) / len(df) * k).astype(int)
