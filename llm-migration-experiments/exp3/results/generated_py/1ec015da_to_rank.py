import polars as pl

df = pl.DataFrame({primary_key.name: primary_key, score.name: score})
df = df.sort(by=str(score.name), descending=not ascending)
df = df.with_columns(
    (
        (
            pl.int_range(1, pl.len() + 1, eager=False).cast(pl.Float64) / pl.len()
        )
        * k
    )
    .ceil()
    .cast(pl.Int64)
    .alias("rank")
)
