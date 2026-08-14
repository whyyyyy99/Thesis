            old_cluster = pl.read_csv(cluster, sep="\t")
            comb_cluster = new_cluster.join(old_cluster, on="samples", how="inner")

            if comb_cluster.height > 0:
                _ = comb_cluster.select(
                    pl.col("coassembly").apply(lambda x: logging.warn(f"{x} has been previously suggested"))
                    )
