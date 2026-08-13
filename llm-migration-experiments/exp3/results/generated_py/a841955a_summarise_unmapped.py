import polars as pl

read_size = pl.read_csv(snakemake.input.read_size, has_header=False, new_columns=["sample", "read_size"])
read_sizes = dict(zip(read_size["sample"].to_list(), read_size["read_size"].to_list()))
summary = summary.with_columns(
    pl.col("samples").map_elements(
        lambda x: sum([read_sizes[sample] for sample in x.split(",")]),
        return_dtype=pl.Int64,
    ).alias("unmapped_size")
)
