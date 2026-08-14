        results = [
            (r["pro_ac"], r["tx_ac"], r["alt_ac"], r["cds_start_i"]) for r in results
        ]
        return pl.DataFrame(
            results, schema=["pro_ac", "tx_ac", "alt_ac", "cds_start_i"]
        ).unique()
