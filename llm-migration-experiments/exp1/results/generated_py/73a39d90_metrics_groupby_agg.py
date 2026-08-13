import polars as pl

summary = (
    df.group_by("condition")
    .agg(
        [
            pl.col(metric).mean().alias("mean"),
            pl.col(metric).median().alias("median"),
        ]
    )
    .with_columns(pl.all().cast(pl.Float64))
)
mixed_mean_raw = summary.filter(pl.col("condition") == "mixed").select("mean").item()
plaintext_mean_raw = summary.filter(pl.col("condition") == "plaintext").select("mean").item()
mixed_mean = float(mixed_mean_raw)
plaintext_mean = float(plaintext_mean_raw)
