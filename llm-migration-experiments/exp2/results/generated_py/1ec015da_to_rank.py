import numpy as np
import polars as pl

df = pl.DataFrame({primary_key.name: primary_key, score.name: score}).drop(primary_key.name)
df = df.sort(by=str(score.name), descending=not ascending)
if df.height == 0:
    df = df.with_columns(pl.Series("rank", [], dtype=pl.Int64))
else:
    df = df.with_columns(
        (
            (pl.int_range(1, pl.len() + 1, eager=False) / pl.len() * k)
            .ceil()
            .cast(pl.Int64)
        ).alias("rank")
    )