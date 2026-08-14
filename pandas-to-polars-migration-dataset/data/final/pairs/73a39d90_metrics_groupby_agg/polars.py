        summary = df.group_by("condition").agg(
            pl.col(metric).mean().alias("mean"),
            pl.col(metric).median().alias("median"),
        )
        summary_by_condition = {
            row["condition"]: row for row in summary.iter_rows(named=True)
        }
        mixed_mean = float(summary_by_condition["mixed"]["mean"])
        plaintext_mean = float(summary_by_condition["plaintext"]["mean"])
