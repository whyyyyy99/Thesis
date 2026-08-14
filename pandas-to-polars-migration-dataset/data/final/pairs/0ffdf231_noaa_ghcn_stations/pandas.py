import pandas as pd

        df = pd.read_fwf(
            listings_file,
            dtype=str,
            header=None,
            colspecs="infer",
            infer_nrows=np.inf,
        )
        df = pl.from_pandas(df)
        df = df[:, [0, 1, 2, 3, 4, 5, 8]]
