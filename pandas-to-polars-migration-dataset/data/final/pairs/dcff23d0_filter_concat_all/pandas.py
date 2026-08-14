import pandas as pd

    flg = pd.concat(flgs, axis=1).all(axis=1)
    df = ds.to_pandas().loc[flg]
