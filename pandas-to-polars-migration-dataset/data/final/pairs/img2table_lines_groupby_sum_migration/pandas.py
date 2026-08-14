import pandas as pd

df_inter = (df_w_l.groupby(['line_id', 'length'])
                .agg(intersection=('intersection', np.sum))
                .reset_index()
                )
