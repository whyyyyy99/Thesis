    if read_size is not None:
        summary = (
            summary
            .with_columns(sample = pl.col("samples").str.split(","))
            .explode("sample")
            .join(read_size, on="sample", how="left")
            .group_by("coassembly", "samples", "length", "total_targets", "total_size")
            .agg(unmapped_size = pl.sum("read_size"))
        )
