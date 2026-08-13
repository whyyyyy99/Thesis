import polars as pl


def before_binned_unbinned(
    appraised: pl.DataFrame,
    pipe_read: pl.DataFrame,
    output_columns: list,
) -> tuple:
    binned = (
        appraised.filter(pl.col("binned"))
        .drop(["divergence", "binned"])
    )
    unbinned = pipe_read.join(
        appraised,
        on=output_columns[0:-1],
    )
    unbinned = (
        unbinned.filter(~pl.col("binned").fill_null(False))
        .drop(["divergence", "binned"])
    )
    unbinned = unbinned.with_columns(pl.lit(None).alias("found_in"))
    return binned, unbinned
