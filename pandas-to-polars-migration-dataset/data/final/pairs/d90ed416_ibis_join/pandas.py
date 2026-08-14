import pandas as pd

            old_cluster = pd.read_csv(cluster, sep="\t")
            comb_cluster = (
                new_cluster
                .set_index("samples")[["coassembly"]]
                .join(old_cluster.set_index("samples")[["length"]], how="inner")
                )
            if not comb_cluster.empty:
                comb_cluster.apply(lambda x: logging.warn(f"{x['coassembly']} has been previously suggested"), axis=1)
