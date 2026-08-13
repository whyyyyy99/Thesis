import polars as pl

sim_results = pl.concat([sim_plaintext, sim_mixed], how="vertical")
sim_results.write_csv(results_dir / "simpy_results.csv")
