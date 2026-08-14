import pandas as pd

    return pd.read_csv(stream, index_col=0,
                       dtype={'age': int,
                              'qx': float,
                              'gender': str})
