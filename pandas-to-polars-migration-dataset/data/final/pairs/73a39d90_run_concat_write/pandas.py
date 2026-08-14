import pandas as pd

    sim_results = pd.concat([sim_plaintext, sim_mixed], ignore_index=True)
    sim_results.to_csv(results_dir / "simpy_results.csv", index=False)
