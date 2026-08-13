import numpy as np
import polars as pl

df = pl.DataFrame({primary_key.name: primary_key, score.name: score})
df = df.sort(score.name, descending=not ascending)
n = df.height
df = df.with_columns(
    pl.Series(
        "rank",
        np.ceil(np.arange(1, n + 1) / n * k).astype(int) if n > 0 else np.array([], dtype=int),
    )
)
