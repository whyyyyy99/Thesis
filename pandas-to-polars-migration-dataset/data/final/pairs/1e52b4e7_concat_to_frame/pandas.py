import pandas as pd

    df = pd.concat([ds.to_pandas() for ds in ds_list])
