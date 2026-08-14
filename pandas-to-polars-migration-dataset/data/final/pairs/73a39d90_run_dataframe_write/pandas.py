import pandas as pd

    pd.DataFrame(sim_boot).to_csv(
        results_dir / "simpy_bootstrap_effects.csv", index=False
    )
