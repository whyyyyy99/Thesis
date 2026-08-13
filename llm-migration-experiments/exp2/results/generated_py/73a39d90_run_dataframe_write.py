import polars as pl

pl.DataFrame(sim_boot).write_csv(results_dir / "simpy_bootstrap_effects.csv")