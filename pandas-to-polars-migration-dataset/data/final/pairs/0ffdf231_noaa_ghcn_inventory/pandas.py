import pandas as pd

        inventory_df = pd.read_fwf(inventory_file, header=None, colspecs="infer", infer_nrows=np.inf)
        inventory_df = pl.from_pandas(inventory_df)
        inventory_df = inventory_df[:, [0, 4, 5]]
